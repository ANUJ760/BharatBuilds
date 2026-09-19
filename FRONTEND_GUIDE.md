# BharatBuilds — Frontend Implementation Guide

> **Source of truth:** `main` branch backend code.
> **Purpose:** Map every backend capability to frontend pages, API calls, state management, and navigation — so a frontend developer can build the full UI without re-reading the backend.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Dependencies](#2-tech-stack--dependencies)
3. [Environment & Configuration](#3-environment--configuration)
4. [Authentication System (Cognito)](#4-authentication-system-cognito)
5. [Role-Based Access Control (RBAC)](#5-role-based-access-control-rbac)
6. [Backend Data Models (Pydantic → TypeScript)](#6-backend-data-models-pydantic--typescript)
7. [Complete API Reference](#7-complete-api-reference)
8. [Pages & Routes](#8-pages--routes)
9. [User Flows & Navigation Map](#9-user-flows--navigation-map)
10. [State Management Requirements](#10-state-management-requirements)
11. [Real-Time Features (Streaming / Polling)](#11-real-time-features-streaming--polling)
12. [Error Handling Contract](#12-error-handling-contract)
13. [Frontend Directory Structure](#13-frontend-directory-structure)
14. [Page-by-Page Implementation Spec](#14-page-by-page-implementation-spec)
15. [API Client Layer Spec](#15-api-client-layer-spec)
16. [Timeline Tree (React Flow) Spec](#16-timeline-tree-react-flow-spec)

---

## 1. Project Overview

**BharatBuilds** is a "prompt-to-live-app" platform. A user types a plain-language description, the backend's AI agent clarifies ambiguities, plans, generates code, and deploys a live app — all within ~10–20 seconds.

The frontend is a **React + Tailwind + React Flow** SPA that must support:

- Prompt intake with an AI-driven clarification flow
- Real-time build/deploy progress tracking
- A Decision Timeline tree view (the primary differentiator — uses React Flow)
- App sharing via email invite with role-based access
- Live editing (chat-based feature requests that redeploy to the same URL)
- Reverting to any prior timeline step

---

## 2. Tech Stack & Dependencies

From `frontend/package.json` on `main`:

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | ^18.3.0 | UI library |
| `react-dom` | ^18.3.0 | DOM renderer |
| `reactflow` | ^11.11.0 | Decision Timeline tree visualization |
| `vite` | ^5.4.0 | Build tool / dev server |
| `typescript` | ^5.5.0 | Type safety |
| `tailwindcss` | ^3.4.0 | Utility-first CSS |
| `autoprefixer` | ^10.4.0 | PostCSS plugin |
| `postcss` | ^8.4.0 | CSS processing |

### Packages to Add (recommended)

| Package | Purpose |
|---------|---------|
| `react-router-dom` | Client-side routing (Home, AppView, Timeline) |
| `amazon-cognito-identity-js` or `aws-amplify/auth` | Cognito auth (sign-up, OTP, token management) |
| `axios` or native `fetch` wrapper | HTTP client for backend API |
| `zustand` or `@tanstack/react-query` | State management / server state caching |

---

## 3. Environment & Configuration

The frontend needs these environment variables (via `.env` or Vite's `import.meta.env`):

```env
# Backend API base URL
VITE_API_BASE_URL=http://localhost:8000

# Cognito (for client-side auth)
VITE_COGNITO_USER_POOL_ID=ap-south-1_XXXXXXXXX
VITE_COGNITO_APP_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=ap-south-1
```

The backend runs on `http://localhost:8000` in development (FastAPI + Uvicorn) with CORS open to all origins (`allow_origins=["*"]`).

---

## 4. Authentication System (Cognito)

### 4.1 How Auth Works

The backend uses **AWS Cognito** for authentication:

- **Token type:** JWT (ID token or access token)
- **Algorithms:** RS256 (production) / HS256 (testing)
- **Token placement:** `Authorization: Bearer <token>` header
- **JWKS endpoint:** `https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json`

### 4.2 Auth Flows the Frontend Must Support

| Flow | Description | Backend Support |
|------|-------------|-----------------|
| **Sign Up** | New user registration | `cognito_client.create_user()` — admin-created, or standard Cognito hosted UI / SDK |
| **Sign In (OTP/Magic Link)** | Email-based OTP login (no passwords for invited users) | Cognito handles — the frontend uses the Cognito SDK |
| **Token Verification** | Every protected request sends JWT in Bearer header | `verify_cognito_token()` validates signature, issuer, audience, expiry |
| **Token Refresh** | Refresh expired access tokens | Cognito SDK handles via refresh tokens |
| **Invited User Login** | User receives invite email → clicks link → OTP auth | `create_user()` creates Cognito user if not exists; email sent via SES |

### 4.3 Token Contents (Claims)

After verification, the backend extracts:

```typescript
interface AuthUser {
  user_id: string;    // Cognito 'sub' claim
  email: string;      // User's email
  role: 'viewer' | 'editor' | 'owner';  // Highest role from cognito:groups
  groups: string[];   // Raw Cognito group names
  claims: Record<string, any>;  // Full JWT payload
}
```

### 4.4 Frontend Auth Implementation

1. **Store tokens** in memory (or secure httpOnly cookie). Never in localStorage for production.
2. **Attach to every API call:** `Authorization: Bearer <id_token>`
3. **Handle 401 responses:** redirect to login
4. **Handle 403 responses:** show "permission denied" message
5. **On token expiry:** use Cognito SDK to silently refresh

---

## 5. Role-Based Access Control (RBAC)

### 5.1 Role Hierarchy

```
owner (level 2) > editor (level 1) > viewer (level 0)
```

Each higher role inherits all permissions of lower roles.

### 5.2 Cognito Groups → Roles

The backend maps Cognito user groups to roles:
- Group `"Owner"` → role `"owner"`
- Group `"Editor"` → role `"editor"`
- Group `"Viewer"` → role `"viewer"`
- No group → defaults to `"viewer"`

### 5.3 Which Endpoints Require Which Roles

| Endpoint | Min Role Required | Auth Dependency |
|----------|-------------------|-----------------|
| `POST /deploy/{app_id}` | `editor` | `require_editor` |
| `POST /apps/{app_id}/revert/{step_id}` | `editor` | `require_editor` |
| `POST /apps/{app_id}/invite` | `editor` | `require_editor` |
| `POST /share/{app_id}/invite` | `editor` | `require_editor` |
| `GET /apps/{app_id}/timeline` | none (public) | — |
| `GET /apps/{app_id}/timeline/{step_id}` | none (public) | — |
| `GET /deploy/{app_id}/status` | none (public) | — |
| `POST /apps/clarify` | none (public) | — |
| `POST /apps/` | none (public) | — |
| `GET /apps/` | none (public) | — |
| `GET /apps/{app_id}` | none (public) | — |
| `GET /health` | none (public) | — |

### 5.4 Frontend RBAC Responsibilities

- **Show/hide UI elements** based on role (e.g., "Revert" button only for editors+)
- **Show/hide "Invite" functionality** — only editors+ can invite
- **Show/hide "Deploy" button** — only editors+ can trigger deploys
- **Viewer-only mode** — viewers can see everything but can't mutate

---

## 6. Backend Data Models (Pydantic → TypeScript)

### 6.1 Enums

```typescript
// AppStatus — lifecycle of a deployed app
type AppStatus = 'pending' | 'building' | 'deployed' | 'failed';

// StepType — type of an agent pipeline step
type StepType = 'clarify' | 'plan' | 'tool_call' | 'codegen' | 'retry' | 'deploy' | 'revert';

// StepStatus — outcome of a timeline step
type StepStatus = 'ok' | 'error' | 'reverted';

// Role — access roles for shared apps
type Role = 'viewer' | 'editor' | 'owner';
```

### 6.2 Core Models

```typescript
/** A deployed user app */
interface App {
  app_id: string;              // UUID, auto-generated
  owner_id: string;            // Required
  title: string;               // 1–200 chars
  prompt: string;              // Min 1 char — the original user request
  live_url: string | null;     // URL where the app is deployed
  status: AppStatus;           // Default: 'pending'
  created_at: string;          // ISO 8601 UTC
  updated_at: string;          // ISO 8601 UTC
}

/** A single node in the decision timeline (tree structure) */
interface TimelineStep {
  app_id: string;
  step_id: string;                    // UUID, auto-generated
  parent_step_id: string | null;      // Links to parent step → forms a TREE
  step_type: StepType;
  input_text: string | null;          // What was fed to this step
  reasoning: string | null;           // Agent's reasoning / explanation
  code_snapshot: string | null;       // Full code at this point
  code_diff: string | null;           // Diff summary (e.g., "+42 lines")
  latency_ms: number | null;          // ≥0, milliseconds
  token_usage: number | null;         // ≥0, token count
  status: StepStatus;                 // Default: 'ok'
  error_message: string | null;
  created_at: string;                 // ISO 8601 UTC
}

/** An invitation to share an app */
interface Invite {
  app_id: string;
  email: string;              // 3–254 chars
  role: Role;                 // Default: 'viewer'
  invited_at: string;         // ISO 8601 UTC
}

/** A single clarifying question */
interface ClarifyQuestion {
  question: string;
  suggested_default: string;
  why_it_matters: string;
}

/** Result of the ambiguity-check pass */
interface ClarifyResponse {
  needs_clarification: boolean;
  questions: ClarifyQuestion[];  // 0–3 questions
}
```

---

## 7. Complete API Reference

**Base URL:** `http://localhost:8000` (dev) / production API Gateway URL

**Common Headers for all requests:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>` (for protected endpoints)

**Common Response Headers:**
- `X-Request-ID: <uuid>` — for tracing/debugging

---

### 7.1 Health Check

```
GET /health
```

**Auth:** None

**Response (200):**
```json
{
  "status": "ok",
  "config": {
    "aws_region": true,
    "bedrock_model_id": true,
    "dynamodb_table_name": true,
    "s3_assets_bucket": true,
    "cognito_user_pool_id": true,
    "cognito_app_client_id": true,
    "ses_sender_email": true,
    "deploy_lambda_function_name": true
  }
}
```

**Frontend use:** Call on app startup to verify backend is reachable. Show connection error if it fails.

---

### 7.2 Clarify Prompt

```
POST /apps/clarify
```

**Auth:** None

**Request Body:**
```json
{
  "prompt": "Build me a todo app"
}
```

**Response (200):**
```json
{
  "needs_clarification": true,
  "questions": [
    {
      "question": "Should the app support multiple users or just one?",
      "suggested_default": "Single user",
      "why_it_matters": "Multi-user requires authentication and separate data stores"
    }
  ]
}
```

If `needs_clarification` is `false`, `questions` will be `[]`.

**Frontend use:** Call this FIRST after user submits a prompt. If questions come back, show them as interactive chips/cards with tap-to-accept defaults.

---

### 7.3 Create App

```
POST /apps/
```

**Auth:** None

**Request Body:**
```json
{
  "prompt": "Build me a todo app",
  "owner_id": "user-uuid-here",
  "title": "My Todo App"          // optional, defaults to "App {id[:8]}"
}
```

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "owner_id": "user-uuid-here",
  "title": "My Todo App",
  "prompt": "Build me a todo app",
  "status": "pending"
}
```

**Frontend use:** Call this to register a new app entry. Use the returned `app_id` for all subsequent calls (deploy, timeline, share).

---

### 7.4 List Apps

```
GET /apps/
```

**Auth:** None

**Response (200):**
```json
{
  "apps": []
}
```

> **Note:** This is currently a placeholder returning an empty list. The frontend should still build the dashboard grid/list for when this is populated.

---

### 7.5 Get App Details

```
GET /apps/{app_id}
```

**Auth:** None

**Path Params:** `app_id` (string, UUID)

**Response (200):** Full app metadata from DynamoDB (matches `App` model shape + any extra DynamoDB attributes)

**Response (404):**
```json
{
  "error": "HTTPException",
  "message": "App not found",
  "detail": "App not found",
  "request_id": "..."
}
```

---

### 7.6 Deploy App (Full Pipeline)

```
POST /deploy/{app_id}
```

**Auth:** `editor` role required (Bearer token)

**Request Body:**
```json
{
  "prompt": "Build me a todo app with due dates",
  "owner_id": "user-uuid",
  "title": "Todo App",                         // optional
  "clarifications": {                           // optional
    "Should the app support multiple users?": "Single user",
    "Do you need due dates?": "Yes, with reminders"
  }
}
```

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "live_url": "https://xxxxx.lambda-url.ap-south-1.on.aws/",
  "status": "deployed",
  "steps_logged": 5
}
```

**Response (500):**
```json
{
  "error": "HTTPException",
  "message": "Code generation failed — see timeline for details",
  "detail": "Code generation failed — see timeline for details",
  "request_id": "..."
}
```

**What happens internally (for progress tracking context):**
1. **Plan step** — Agent creates a plan from the prompt + clarifications
2. **Codegen step** — Agent generates Python source code
3. **Review step** — Agent reviews code for errors (tool_call type)
4. **Retry steps** (0–2) — If review fails, agent retries with fix instructions
5. **Deploy step** — Code is packaged as a zip and deployed to Lambda

**Frontend use:** This is the MAIN action endpoint. After calling, redirect user to AppView. Poll `/deploy/{app_id}/status` for status updates while waiting. Then load the timeline.

---

### 7.7 Deploy Status

```
GET /deploy/{app_id}/status
```

**Auth:** None

**Path Params:** `app_id` (string)

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "status": "deployed",       // or "pending", "building", "failed"
  "live_url": "https://xxxxx.lambda-url.ap-south-1.on.aws/"
}
```

**Response (404):** App not found

**Frontend use:** Poll this endpoint every 2–3 seconds after triggering a deploy, until `status` changes from `"pending"`/`"building"` to `"deployed"` or `"failed"`.

---

### 7.8 Get Full Timeline

```
GET /apps/{app_id}/timeline
```

**Auth:** None

**Path Params:** `app_id` (string)

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "step_count": 5,
  "steps": [
    {
      "app_id": "a1b2c3d4-...",
      "step_id": "step-uuid-1",
      "parent_step_id": null,
      "step_type": "plan",
      "input_text": "Build me a todo app...",
      "reasoning": "{'components': ['TodoList', ...]}",
      "code_snapshot": null,
      "code_diff": null,
      "latency_ms": 2340,
      "token_usage": 512,
      "status": "ok",
      "error_message": null,
      "created_at": "2026-09-19T17:00:00+00:00"
    },
    {
      "step_id": "step-uuid-2",
      "parent_step_id": "step-uuid-1",
      "step_type": "codegen",
      "code_snapshot": "import flask\n...",
      "code_diff": "+42 lines",
      "latency_ms": 5200,
      "status": "ok"
    }
  ]
}
```

**Key property:** Steps form a **tree** via `parent_step_id`. The root step has `parent_step_id: null`. Branches occur on retries and reverts.

**Frontend use:** Feed this data into React Flow to render the Decision Timeline tree. Each step is a node, `parent_step_id` defines edges.

---

### 7.9 Get Single Timeline Step

```
GET /apps/{app_id}/timeline/{step_id}
```

**Auth:** None

**Path Params:** `app_id` (string), `step_id` (string)

**Response (200):** Full `TimelineStep` object (see model above)

**Response (404):** Step not found

**Frontend use:** Load detailed step info when a user clicks a node in the timeline tree. Show the code snapshot, reasoning, latency, token usage, etc. in a side panel.

---

### 7.10 Revert to Step

```
POST /apps/{app_id}/revert/{step_id}
```

**Auth:** `editor` role required (Bearer token)

**Path Params:** `app_id` (string), `step_id` (string)

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "reverted_to_step": "step-uuid-2",
  "revert_step_id": "step-uuid-new",
  "live_url": "https://xxxxx.lambda-url.ap-south-1.on.aws/",
  "status": "reverted"
}
```

**Response (400):**
```json
{
  "error": "HTTPException",
  "message": "Target step does not contain a code snapshot to revert to",
  "detail": "...",
  "request_id": "..."
}
```

**Response (404):** Step not found

**What happens:** The backend fetches the `code_snapshot` from the target step, redeploys it to Lambda, and logs a new timeline node of type `revert` with `status: reverted`.

**Frontend use:** Show a "Revert to this version" button on timeline steps that have `code_snapshot != null`. After revert, reload the timeline (a new `revert` node will appear). Refresh the live app URL.

---

### 7.11 Invite Collaborator

```
POST /apps/{app_id}/invite
POST /share/{app_id}/invite     ← alias, same handler
```

**Auth:** `editor` role required (Bearer token)

**Request Body:**
```json
{
  "email": "collaborator@example.com",
  "role": "viewer"                       // "viewer" (default) or "editor"
}
```

**Response (200):**
```json
{
  "app_id": "a1b2c3d4-...",
  "email": "collaborator@example.com",
  "role": "viewer",
  "status": "sent",
  "message_id": "ses-message-id"
}
```

**Response (502):**
```json
{
  "error": "HTTPException",
  "message": "Failed to send invite email: ...",
  "detail": "...",
  "request_id": "..."
}
```

**What happens on the backend:**
1. Creates/ensures Cognito user for the email
2. Adds user to "Viewer" or "Editor" Cognito group
3. Persists invite in DynamoDB (key: `app_id` + `invite#{email}`)
4. Sends HTML invite email via SES with a link to `https://bharatbuilds.dev/apps/{app_id}`

**Frontend use:** Show an "Invite" modal/form with email input and role selector (dropdown: Viewer / Editor). Display success/error feedback after submission.

---

## 8. Pages & Routes

Based on the existing frontend stubs and backend capabilities, the app needs these pages:

| # | Route | Page Component | Purpose | Auth Required |
|---|-------|---------------|---------|---------------|
| 1 | `/` | `Home` | Prompt intake + clarification flow | No (but shows login) |
| 2 | `/login` | `Login` | Cognito auth (OTP/email) | No |
| 3 | `/apps/{app_id}` | `AppView` | Single app: status, live URL, share, live edit chat | Recommended |
| 4 | `/apps/{app_id}/timeline` | `Timeline` | Full-screen Decision Timeline tree + step detail side panel + revert | Recommended |
| 5 | `/dashboard` | `Dashboard` | List all user's apps (when list endpoint is populated) | Yes |

### Route Configuration (React Router)

```typescript
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/login" element={<Login />} />
  <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
  <Route path="/apps/:appId" element={<AppView />} />
  <Route path="/apps/:appId/timeline" element={<Timeline />} />
</Routes>
```

---

## 9. User Flows & Navigation Map

### 9.1 Primary Flow: Prompt → Deployed App

```
Home (/)
  │
  ├─ User types prompt
  ├─ POST /apps/clarify
  │   ├─ needs_clarification: false → skip to Create
  │   └─ needs_clarification: true → show question chips
  │       └─ User answers (tap default or type)
  │
  ├─ POST /apps/ (create app entry, get app_id)
  │
  ├─ POST /deploy/{app_id} (trigger full pipeline)
  │   ← requires editor auth; if not logged in, prompt login first
  │
  ├─ REDIRECT → /apps/{app_id}
  │
  AppView (/apps/{app_id})
  │
  ├─ Poll GET /deploy/{app_id}/status every 2–3s
  │   ├─ status: pending/building → show progress indicator
  │   ├─ status: deployed → show live_url, enable all features
  │   └─ status: failed → show error, offer retry
  │
  ├─ Show live app in iframe (live_url)
  ├─ Show "Share" button → opens invite modal
  ├─ Show "Timeline" button → navigates to /apps/{app_id}/timeline
  └─ Show chat input for live edits (re-triggers deploy pipeline)
```

### 9.2 Timeline & Revert Flow

```
Timeline (/apps/{app_id}/timeline)
  │
  ├─ GET /apps/{app_id}/timeline → full step list
  ├─ Render as React Flow tree (parent_step_id → edges)
  │
  ├─ User clicks a node
  │   └─ GET /apps/{app_id}/timeline/{step_id} → detail panel
  │       ├─ Shows: step_type, reasoning, code_snapshot, latency, tokens, status
  │       └─ If code_snapshot exists & user is editor+:
  │           └─ Show "Revert to this version" button
  │               └─ POST /apps/{app_id}/revert/{step_id}
  │                   └─ Reload timeline (new revert node appears)
  │                   └─ Show success message with new live_url
  │
  └─ Back button → /apps/{app_id}
```

### 9.3 Share Flow

```
AppView (/apps/{app_id})
  │
  ├─ User clicks "Share" (must be editor+)
  │   └─ Opens invite modal:
  │       ├─ Email input
  │       ├─ Role selector: Viewer / Editor
  │       └─ "Send Invite" button
  │           └─ POST /apps/{app_id}/invite
  │               ├─ Success: show "Invite sent to {email}"
  │               └─ Failure: show error message
  │
  │   Invited user flow:
  │   └─ Receives email with link to /apps/{app_id}
  │       └─ Clicks link → lands on /apps/{app_id}
  │           └─ If not authenticated → redirect to /login
  │               └─ OTP login with their email
  │                   └─ Cognito creates session with Viewer/Editor group
  │                       └─ Redirect back to /apps/{app_id}
```

### 9.4 Login Flow

```
/login
  │
  ├─ Email input
  ├─ "Send OTP" → Cognito SDK initiates auth
  ├─ OTP input screen
  ├─ "Verify" → Cognito SDK completes auth
  ├─ Store tokens
  └─ Redirect to:
      ├─ stored return URL (if redirected from protected page)
      └─ or / (Home)
```

### 9.5 Redirections Summary

| From | To | Condition |
|------|----|-----------|
| `/` | `/apps/{app_id}` | After successful deploy trigger |
| `/apps/{app_id}` | `/login?return=/apps/{app_id}` | If auth required action attempted without auth |
| `/login` | stored `returnUrl` or `/` | After successful authentication |
| `/apps/{app_id}` | `/apps/{app_id}/timeline` | User clicks "Timeline" button |
| `/apps/{app_id}/timeline` | `/apps/{app_id}` | User clicks "Back" or app title |
| email invite link | `/apps/{app_id}` | Invited user clicks link in email |

---

## 10. State Management Requirements

### 10.1 Global State

```typescript
interface GlobalState {
  // Auth
  auth: {
    isAuthenticated: boolean;
    user: AuthUser | null;       // user_id, email, role, groups
    tokens: {
      idToken: string;
      accessToken: string;
      refreshToken: string;
    } | null;
    isLoading: boolean;
  };
}
```

### 10.2 Per-Page State

**Home Page:**
```typescript
interface HomeState {
  prompt: string;
  clarifyResponse: ClarifyResponse | null;
  clarifications: Record<string, string>;  // question → answer map
  isSubmitting: boolean;
  isClarifying: boolean;
}
```

**AppView Page:**
```typescript
interface AppViewState {
  app: App | null;
  deployStatus: 'pending' | 'building' | 'deployed' | 'failed' | null;
  liveUrl: string | null;
  isLoading: boolean;
  isDeploying: boolean;
  // For live edit chat
  editPrompt: string;
  isEditing: boolean;
}
```

**Timeline Page:**
```typescript
interface TimelineState {
  steps: TimelineStep[];
  stepCount: number;
  selectedStepId: string | null;
  selectedStepDetail: TimelineStep | null;
  isLoadingTimeline: boolean;
  isLoadingDetail: boolean;
  isReverting: boolean;
}
```

---

## 11. Real-Time Features (Streaming / Polling)

### 11.1 Deploy Status Polling (`useDeployStatus` hook)

The backend does NOT have WebSocket/SSE for deploy status. Use **polling**:

```typescript
function useDeployStatus(appId: string) {
  // Poll GET /deploy/{app_id}/status every 2-3 seconds
  // Stop polling when status is "deployed" or "failed"
  // Return: { status, liveUrl, isPolling }
}
```

### 11.2 Agent Stream (`useAgentStream` hook)

The backend does NOT currently expose an SSE/WebSocket stream for agent steps.

**Recommended approach:**
- After deploy is triggered, poll `GET /apps/{app_id}/timeline` every 3–5 seconds
- Compare step counts to detect new steps appearing
- Once deploy is complete (from status polling), stop timeline polling
- Alternatively, prepare for future SSE/WebSocket support by abstracting the data source

```typescript
function useAgentStream(appId: string) {
  // Poll GET /apps/{app_id}/timeline periodically
  // Emit new steps as they appear
  // Return: { steps, isStreaming, latestStep }
}
```

### 11.3 Timeline Tree Live Updates

During an active build:
1. Poll timeline endpoint every 3 seconds
2. When new steps appear, animate them into the React Flow tree
3. The `motion.css` design system has provisions for "timeline node animating in" as the key motion moment

---

## 12. Error Handling Contract

All backend errors follow this consistent shape:

```typescript
interface APIError {
  error: string;         // Error type: "HTTPException", "ValidationError", "InternalServerError"
  message: string;       // Human-readable message
  detail: any;           // Detailed info (string or array for validation errors)
  request_id: string;    // UUID for debugging / support
}
```

### HTTP Status Codes

| Code | Meaning | Frontend Action |
|------|---------|-----------------|
| 200 | Success | Process response |
| 401 | Unauthorized (missing/invalid token) | Redirect to `/login` |
| 403 | Forbidden (insufficient role) | Show "Permission denied" message |
| 404 | Resource not found | Show "Not found" page/message |
| 422 | Validation error | Show field-level errors from `detail` array |
| 500 | Server error | Show generic error with `request_id` for support |
| 502 | Bad gateway (SES/external service failure) | Show service error message |

### Validation Error Detail Format (422)

```json
{
  "error": "ValidationError",
  "message": "Invalid request parameters or payload",
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "request_id": "..."
}
```

---

## 13. Frontend Directory Structure

From the `main` branch, these directories and files exist (with `.gitkeep` placeholders). Fill them out:

```
frontend/src/
├── main.tsx                    # App entry point
├── App.tsx                     # Root component with router
│
├── api/                        # Typed API client layer
│   ├── client.ts               # Base HTTP client (fetch/axios wrapper with auth)
│   ├── apps.ts                 # App CRUD API calls
│   ├── deploy.ts               # Deploy API calls
│   ├── timeline.ts             # Timeline API calls
│   ├── share.ts                # Invite API calls
│   └── types.ts                # All TypeScript types matching backend models
│
├── hooks/
│   ├── useAgentStream.ts       # Real-time agent step stream (polling)
│   ├── useDeployStatus.ts      # Deploy status polling
│   ├── useAuth.ts              # Cognito auth state & methods
│   └── useTimeline.ts          # Timeline data fetching & tree conversion
│
├── pages/
│   ├── Home.tsx                # Prompt intake + clarify flow
│   ├── Login.tsx               # Cognito OTP login
│   ├── AppView.tsx             # Single app: status, share, live edit
│   ├── Timeline.tsx            # Full-screen decision tree + revert
│   └── Dashboard.tsx           # App list (future)
│
├── components/
│   ├── ui/                     # Primitives: Button, Input, Modal, Chip, Spinner, Badge
│   ├── chat/                   # Prompt box, clarifying-question chips, edit chat input
│   ├── timeline/               # React Flow tree, step detail panel, revert button
│   ├── dashboard/              # App cards, deploy status badge, share modal
│   └── layout/                 # Shell, nav, page containers
│
├── design/
│   ├── tokens.css              # Color, type, spacing tokens (exists)
│   ├── typography.css          # Typography system (exists)
│   └── motion.css              # Single deliberate motion moment (exists)
│
└── lib/
    ├── auth.ts                 # Cognito SDK wrapper
    └── constants.ts            # API URLs, polling intervals, etc.
```

---

## 14. Page-by-Page Implementation Spec

### 14.1 Home Page (`/`)

**Purpose:** Single-purpose prompt intake. Intentionally minimal — a single input, not a dashboard.

**Backend API Calls:**
1. `POST /apps/clarify` — on prompt submit
2. `POST /apps/` — after clarifications resolved (or skipped)
3. `POST /deploy/{app_id}` — trigger build

**Functional Requirements:**
- Large centered prompt input (textarea or auto-expanding input)
- "Build" / "Create" submit button
- On submit: call `/apps/clarify`
  - If `needs_clarification: true`: show question cards/chips below the input
    - Each card shows: `question`, `suggested_default` (as a tappable chip), `why_it_matters`
    - User can tap the default or type their own answer
    - Collect all answers into `clarifications: Record<string, string>`
  - If `needs_clarification: false`: proceed directly
- After clarifications resolved: call `POST /apps/` → get `app_id` → call `POST /deploy/{app_id}` → redirect to `/apps/{app_id}`
- Show loading state during API calls
- If deploy auth fails (401): redirect to `/login?return=/` with prompt saved

**Data Needed:**
- User auth state (for deploy call)

---

### 14.2 Login Page (`/login`)

**Purpose:** Email + OTP authentication via Cognito

**Backend API Calls:** None directly — uses Cognito SDK

**Functional Requirements:**
- Email input field
- "Send Code" button → initiates Cognito auth
- OTP input (6-digit code field)
- "Verify" button → confirms auth code
- On success: store tokens → redirect to `returnUrl` query param or `/`
- On error: show error message
- Link to go back home without logging in

---

### 14.3 AppView Page (`/apps/{app_id}`)

**Purpose:** Single deployed app's dashboard — status, live preview, sharing, live editing

**Backend API Calls:**
1. `GET /apps/{app_id}` — load app metadata
2. `GET /deploy/{app_id}/status` — poll status (via `useDeployStatus`)
3. `POST /apps/{app_id}/invite` — invite collaborator (editor+ only)
4. `POST /deploy/{app_id}` — live edit / re-deploy (editor+ only)

**Functional Requirements:**
- **App header:** title, status badge, `app_id` (copyable)
- **Status area:**
  - `pending` / `building`: show animated progress indicator, poll for updates
  - `deployed`: show live URL (clickable, copyable), "Open" button
  - `failed`: show error message, "Retry" button
- **Live preview:** `<iframe>` embedding the `live_url` (when deployed)
- **Share section (editor+ only):**
  - "Invite" button → opens modal with email + role selector
  - Role options: Viewer, Editor
  - Send button → `POST /apps/{app_id}/invite`
  - Success/error feedback
- **Timeline link:** "View Decision Timeline" button → navigate to `/apps/{app_id}/timeline`
- **Live Edit (editor+ only):**
  - Chat-style input for feature requests
  - On submit: call `POST /deploy/{app_id}` with new prompt + same `app_id`
  - Show building progress, reload iframe when done
- **Prompt display:** show the original prompt that created this app

---

### 14.4 Timeline Page (`/apps/{app_id}/timeline`)

**Purpose:** Full-screen Decision Timeline tree view with step inspection and revert capability. This is the **primary UI differentiator** — give it the most attention.

**Backend API Calls:**
1. `GET /apps/{app_id}/timeline` — load all steps
2. `GET /apps/{app_id}/timeline/{step_id}` — load step detail on click
3. `POST /apps/{app_id}/revert/{step_id}` — revert to a step (editor+ only)

**Functional Requirements:**

- **React Flow tree visualization:**
  - Each `TimelineStep` is a node
  - `parent_step_id` defines parent → child edges
  - Root node(s) have `parent_step_id: null`
  - Node appearance varies by `step_type`:
    - `plan` — planning icon/color
    - `codegen` — code icon/color
    - `tool_call` — review/tool icon/color
    - `retry` — retry/warning icon/color
    - `deploy` — deploy/rocket icon/color
    - `revert` — undo/revert icon/color
  - Node shows `status` via color/badge: `ok` (green), `error` (red), `reverted` (orange)
  - Node label shows `step_type` and brief timing info (`latency_ms`)

- **Step detail side panel:**
  - Opens when a node is clicked
  - Shows ALL fields:
    - `step_type` — type badge
    - `reasoning` — the agent's explanation (can be long, scrollable)
    - `input_text` — what was fed to this step
    - `code_snapshot` — syntax-highlighted code viewer (if present)
    - `code_diff` — diff summary
    - `latency_ms` — formatted (e.g., "2.3s")
    - `token_usage` — token count
    - `status` — status badge
    - `error_message` — error details (if present, red)
    - `created_at` — formatted timestamp
  - **"Revert to this version" button** (editor+ only)
    - Only visible when `code_snapshot` is not null
    - Confirmation dialog: "This will redeploy the app to this version. Continue?"
    - On confirm: `POST /apps/{app_id}/revert/{step_id}`
    - On success: reload timeline, show new revert node, display success message with new live URL

- **Timeline header:**
  - Back navigation to `/apps/{app_id}`
  - App title + app_id
  - Step count badge
  - Zoom controls (React Flow built-in)

- **Live update during active builds:**
  - Poll timeline endpoint every 3s during active builds
  - New nodes should animate in (use `motion.css`)

---

### 14.5 Dashboard Page (`/dashboard`)

**Purpose:** List all user's apps (future — currently list endpoint returns `[]`)

**Backend API Calls:**
1. `GET /apps/` — list apps

**Functional Requirements:**
- Grid/list of app cards
- Each card shows: title, status badge, created_at, live_url if deployed
- Click → navigate to `/apps/{app_id}`
- "Create New" button → navigate to `/`
- Empty state: "No apps yet. Create your first app!"

---

## 15. API Client Layer Spec

### 15.1 Base Client

```typescript
// api/client.ts

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();  // from auth store
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    // error shape: { error, message, detail, request_id }
    throw new APIError(response.status, error);
  }

  return response.json();
}
```

### 15.2 API Functions

```typescript
// api/apps.ts
export const clarifyPrompt = (prompt: string) =>
  apiRequest<ClarifyResponse>('/apps/clarify', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
  });

export const createApp = (data: { prompt: string; owner_id: string; title?: string }) =>
  apiRequest<{ app_id: string; owner_id: string; title: string; prompt: string; status: string }>('/apps/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const getApp = (appId: string) =>
  apiRequest<App>(`/apps/${appId}`);

export const listApps = () =>
  apiRequest<{ apps: App[] }>('/apps/');

// api/deploy.ts
export const deployApp = (appId: string, data: {
  prompt: string;
  owner_id: string;
  title?: string;
  clarifications?: Record<string, string>;
}) =>
  apiRequest<{ app_id: string; live_url: string; status: string; steps_logged: number }>(
    `/deploy/${appId}`,
    { method: 'POST', body: JSON.stringify(data) }
  );

export const getDeployStatus = (appId: string) =>
  apiRequest<{ app_id: string; status: string; live_url: string | null }>(
    `/deploy/${appId}/status`
  );

// api/timeline.ts
export const getTimeline = (appId: string) =>
  apiRequest<{ app_id: string; step_count: number; steps: TimelineStep[] }>(
    `/apps/${appId}/timeline`
  );

export const getTimelineStep = (appId: string, stepId: string) =>
  apiRequest<TimelineStep>(
    `/apps/${appId}/timeline/${stepId}`
  );

export const revertToStep = (appId: string, stepId: string) =>
  apiRequest<{
    app_id: string;
    reverted_to_step: string;
    revert_step_id: string;
    live_url: string;
    status: string;
  }>(`/apps/${appId}/revert/${stepId}`, { method: 'POST' });

// api/share.ts
export const inviteUser = (appId: string, data: { email: string; role?: Role }) =>
  apiRequest<{
    app_id: string;
    email: string;
    role: string;
    status: string;
    message_id: string;
  }>(`/apps/${appId}/invite`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
```

---

## 16. Timeline Tree (React Flow) Spec

### 16.1 Converting Steps to React Flow Nodes/Edges

```typescript
import { Node, Edge } from 'reactflow';

function stepsToFlow(steps: TimelineStep[]): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = steps.map((step, index) => ({
    id: step.step_id,
    type: 'timelineNode',  // custom node type
    position: { x: 0, y: index * 120 },  // auto-layout recommended (dagre)
    data: {
      stepType: step.step_type,
      status: step.status,
      latencyMs: step.latency_ms,
      tokenUsage: step.token_usage,
      hasCodeSnapshot: !!step.code_snapshot,
      errorMessage: step.error_message,
      createdAt: step.created_at,
    },
  }));

  const edges: Edge[] = steps
    .filter(step => step.parent_step_id)
    .map(step => ({
      id: `${step.parent_step_id}-${step.step_id}`,
      source: step.parent_step_id!,
      target: step.step_id,
      animated: step.status === 'ok',
    }));

  return { nodes, edges };
}
```

### 16.2 Tree Layout

Use `dagre` library for automatic tree layout:

```bash
npm install dagre @types/dagre
```

Layout steps as a **top-to-bottom tree** with branches where retries or reverts create alternate paths.

### 16.3 Node Type Styling Guide

| `step_type` | Icon Concept | Color Theme |
|-------------|-------------|-------------|
| `clarify` | Question mark / chat bubble | Blue |
| `plan` | Blueprint / clipboard | Indigo |
| `codegen` | Code brackets / terminal | Green |
| `tool_call` | Magnifying glass / check | Purple |
| `retry` | Refresh / retry arrow | Amber/Yellow |
| `deploy` | Rocket / cloud-upload | Emerald |
| `revert` | Undo / clock-rewind | Orange |

### 16.4 Node Status Indicators

| `status` | Visual | Meaning |
|----------|--------|---------|
| `ok` | Green dot/border | Step completed successfully |
| `error` | Red dot/border | Step failed |
| `reverted` | Orange dot/border | This step was a revert action |

---

## Quick Reference: Complete Endpoint ↔ Page Mapping

| Endpoint | Method | Page(s) That Use It | When |
|----------|--------|---------------------|------|
| `GET /health` | GET | App startup (any page) | Once on load |
| `POST /apps/clarify` | POST | Home | On prompt submit |
| `POST /apps/` | POST | Home | After clarification |
| `GET /apps/` | GET | Dashboard | On page load |
| `GET /apps/{app_id}` | GET | AppView | On page load |
| `POST /deploy/{app_id}` | POST | Home, AppView (live edit) | On deploy/edit |
| `GET /deploy/{app_id}/status` | GET | AppView | Polling during build |
| `GET /apps/{app_id}/timeline` | GET | Timeline | On page load + polling |
| `GET /apps/{app_id}/timeline/{step_id}` | GET | Timeline | On node click |
| `POST /apps/{app_id}/revert/{step_id}` | POST | Timeline | On revert button |
| `POST /apps/{app_id}/invite` | POST | AppView | On invite submit |

---

> **Note:** This guide covers everything the backend exposes on `main`. No UI design decisions are included — only functional requirements, data flows, and API contracts. The person implementing the UI should use this as the complete specification for what the frontend must do.
