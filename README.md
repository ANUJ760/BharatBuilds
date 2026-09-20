# [Project Name TBD]

> SmallOps — turn a plain-language prompt into a live, authenticated, shareable web app in under a minute, deployed on real AWS infrastructure, with a full visual record of every decision the agent made along the way.

Built for **Bharat Builds Tour 2026 (First Commit)** by WeMakeDevs × AWS.

---

## 1. The Problem

AI agents can now write a working app from a prompt in seconds — a form, a tracker, a small internal tool. But turning that generated code into something a real person can actually *use* still requires:

- A cloud account and DevOps knowledge to deploy it
- Manually wiring up authentication
- A database or storage layer, even for something tiny
- A way to share it with teammates that isn't "send them a zip file"
- Trust that when you ask the agent to change something, it won't silently break what already worked

Incumbent clouds (AWS, Azure, GCP) were built for **Big Software** — systems designed to scale to millions of users, at the cost of significant setup complexity. Most AI-generated apps are the opposite: **SmallOps** — purpose-built tools for one person or a small team, that need to be deployed and shared as easily as a Google Doc.

This project is a thin, opinionated cloud layer built specifically for that gap — running entirely on AWS.

---

## 2. Core Idea

1. A user describes what they want in plain language.
2. The agent checks whether the request is ambiguous in ways that would materially change the app, and asks up to 3 quick questions if so — otherwise it proceeds immediately.
3. The agent plans, writes, and deploys the app to a live AWS-hosted URL.
4. The app is wrapped in authentication and sharing out of the box — no code changes needed.
5. Every step the agent took (reasoning, tool calls, code generated, retries) is recorded as a node in a visual decision timeline.
6. The user can inspect any past step and **revert the live app to that exact state** if a later change broke something.

---

## 3. Feature Breakdown

### 3.1 Prompt-to-App Generation
- User submits a plain-language request (chat interface).
- Agent generates a working single-purpose app (form + logic + simple UI).
- Powered by **Amazon Bedrock**.

### 3.2 Clarify-Then-Build
- Before generating any code, a fast "ambiguity check" pass runs on the prompt.
- If the request is underspecified in a way that would change the resulting app's structure (data fields, roles/permissions, single vs. multi-user, etc.), the agent asks up to **3** targeted questions, each with a suggested default.
- The user can tap a suggested default or answer directly — no open-ended back-and-forth.
- Once resolved, the build proceeds **without further interruption**.
- This step is itself logged as the first node in the Decision Timeline (see 3.5).

### 3.3 Instant Deploy on AWS
- Generated app code is deployed to a live, publicly reachable URL within ~10–20 seconds.
- Runs in an isolated per-app sandbox (containerized).
- No manual config screens, no user-managed infrastructure.

### 3.4 Zero-Config Sharing & Auth
- Every deployed app is wrapped with authentication — the user never edits the generated app's code to add login.
- Owner can invite others by email/phone; invitees get a lightweight login (magic link / OTP) and a **Viewer** or **Editor** role.
- Sharing an app should feel exactly like sharing a Google Doc: one link, one invite step, no separate cloud account required for collaborators.

### 3.5 Decision Timeline & Backtrack
- Every agent action — plan, tool call, code generation, retry, deploy — is logged as a node in a tree/timeline.
- Nodes are visually connected: the main trunk shows the successful path; retries or corrected mistakes branch off and are visually distinguished.
- Clicking any node opens a side panel showing:
  - What the agent saw as input at that step
  - Its reasoning/plan text
  - The code diff produced (if any)
  - Latency and token usage
  - Status (ok / error / reverted)
- A **"Revert to here"** action re-deploys the exact code snapshot stored at that step, instantly rolling the live app back — no need to re-prompt or replay history.

### 3.6 Live Editing
- Owner can describe a change in chat ("add a summary view", "add a new field").
- Agent edits the existing app and redeploys to the **same URL** — the link never changes.
- Every edit is captured as a new node in the Decision Timeline, so it's always inspectable and revertible.

---

## 4. Architecture

```
                        ┌─────────────────────────┐
                        │   Dashboard (Frontend)   │
                        │   S3 + CloudFront         │
                        └────────────┬─────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │   API Layer              │
                         │   API Gateway + Lambda    │
                         └───────────┬────────────┘
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        │                            │                              │
┌───────▼────────┐        ┌──────────▼──────────┐        ┌─────────▼─────────┐
│  Agent Layer     │        │  Deploy Layer         │        │  Auth Layer         │
│  Amazon Bedrock   │        │  AWS Fargate (ECS)    │        │  Amazon Cognito      │
│  - Clarify pass   │        │  or Lambda Function    │        │  - Magic link/OTP    │
│  - Plan/codegen   │        │    URLs per app        │        │  - Viewer/Editor      │
│  - ReAct loop      │        │  ALB path routing       │        │    roles              │
└───────┬────────┘        └──────────┬──────────┘        └─────────┬─────────┘
        │                            │                              │
        └────────────────────────────┼──────────────────────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │  Data Layer                 │
                       │  DynamoDB                    │
                       │  - App metadata                │
                       │  - Decision timeline / traces   │
                       │  - Code snapshots per step        │
                       │  S3 (generated app assets)          │
                       └───────────────────────────────────┘
```

### AWS Services Used

| Layer | Service | Purpose |
|---|---|---|
| Agent / codegen | **Amazon Bedrock** | Clarify pass, planning, code generation, live edits |
| App runtime | **AWS Fargate (ECS)** | Isolated sandbox per deployed app |
| Alternate/fast-path runtime | **AWS Lambda + Function URLs** | Near-instant deploy for lightweight apps |
| Routing | **Application Load Balancer** / **API Gateway** | Per-app path-based routing to live URLs |
| Auth & sharing | **Amazon Cognito** | Magic link/OTP login, role-based access, wraps generated apps without modifying their code |
| Invites | **Amazon SES** | Email invitations for sharing |
| Data store | **Amazon DynamoDB** | App metadata, decision timeline/trace log, code snapshots |
| Static hosting | **Amazon S3 + CloudFront** | Dashboard frontend, generated static assets |
| Infra-as-code | **AWS CDK** | Reproducible deployment of the platform itself |

---

## 5. Tech Stack

- **Frontend:** React + Tailwind, React Flow (for the Decision Timeline tree view)
- **Backend:** Python + FastAPI (or Lambda-native handlers)
- **Agent runtime:** hand-rolled ReAct loop calling Amazon Bedrock directly
- **Data:** DynamoDB (single-table design, `app_id` + `step_id` sort key for timeline queries)
- **Infra:** AWS CDK

---

## 6. Folder Structure

```
project-root/
├── README.md
├── .env.example
├── .gitignore
│
├── frontend/                          # React + Tailwind dashboard — carries the Best UI track
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── design/                    # design system, kept separate from components
│   │   │   ├── tokens.css             # color, type, spacing tokens
│   │   │   ├── typography.css
│   │   │   └── motion.css             # the one deliberate motion moment, isolated
│   │   ├── components/
│   │   │   ├── ui/                    # low-level primitives: Button, Input, Modal, Chip
│   │   │   ├── chat/                  # prompt box + clarifying-question chips
│   │   │   ├── timeline/              # Decision Timeline tree (React Flow) + side panel
│   │   │   ├── dashboard/             # app cards, deploy status, share modal
│   │   │   └── layout/                # shell, nav, page containers
│   │   ├── pages/
│   │   │   ├── Home.tsx               # prompt intake + clarify flow
│   │   │   ├── AppView.tsx            # single deployed app: status, share, live edit
│   │   │   └── Timeline.tsx           # full-screen decision tree + revert
│   │   ├── hooks/
│   │   │   ├── useAgentStream.ts      # streams agent steps as they happen
│   │   │   └── useDeployStatus.ts
│   │   ├── api/                       # typed client for backend endpoints
│   │   └── lib/
│   ├── tailwind.config.ts
│   ├── package.json
│   └── index.html
│
├── backend/                            # FastAPI (or Lambda handlers)
│   ├── main.py
│   ├── api/
│   │   ├── routes_apps.py             # create/list/get deployed apps
│   │   ├── routes_timeline.py         # GET /apps/{id}/timeline, POST /revert/{step_id}
│   │   ├── routes_share.py            # invites, roles
│   │   └── routes_deploy.py
│   ├── agent/
│   │   ├── clarify.py                 # ambiguity-check pass (structured JSON output)
│   │   ├── planner.py                 # ReAct loop — plan/tool-call/codegen steps
│   │   ├── codegen.py
│   │   ├── bedrock_client.py
│   │   └── trace_logger.py            # writes every agent step to DynamoDB as a timeline node
│   ├── deploy/
│   │   ├── fargate_deployer.py
│   │   ├── lambda_deployer.py         # fast-path deploy for lightweight apps
│   │   └── router.py                  # ALB/API Gateway route registration
│   ├── auth/
│   │   ├── cognito_client.py
│   │   └── roles.py                   # Viewer/Editor enforcement
│   ├── storage/
│   │   ├── dynamodb_client.py
│   │   └── s3_client.py
│   ├── models/                        # Pydantic schemas (App, TimelineStep, Invite, ...)
│   ├── requirements.txt
│   └── tests/
│
├── infra/                              # AWS CDK — deploys the platform itself
│   ├── bin/
│   │   └── app.ts
│   ├── lib/
│   │   ├── network-stack.ts           # VPC, ALB
│   │   ├── compute-stack.ts           # Fargate cluster, Lambda functions
│   │   ├── data-stack.ts              # DynamoDB tables, S3 buckets
│   │   ├── auth-stack.ts              # Cognito user pool, app client
│   │   └── frontend-stack.ts          # S3 + CloudFront
│   ├── cdk.json
│   └── package.json
│
├── generated-app-runtime/              # minimal sandbox template each generated app runs inside
│   ├── Dockerfile
│   └── entrypoint template files
│
└── docs/
    ├── architecture.md                # diagram + service mapping
    ├── demo-script.md                 # clarify → build → edit → backtrack flow
    └── blog/                          # drafts for the AWS Builder Center "Best Blog" entry
```

### Notes for the Best UI track

- **`design/tokens.css`** holds the palette/type/spacing decisions as their own file, not scattered Tailwind classes — keeps the visual identity intentional and easy to review as a whole.
- **One deliberate motion moment**, isolated in `motion.css` — the strongest candidate is the timeline node animating in as the agent completes a step live.
- **`timeline/` is its own component folder**, separate from `dashboard/` — it's the most distinctive UI surface and the strongest Best-UI evidence, so it gets room to be a considered piece rather than a bolt-on panel.
- Keep `Home.tsx` minimal — a single input, not a dashboard shell — so it contrasts cleanly with the richer timeline view later in the demo.

---

## 7. User Flow (End-to-End Demo)

1. **Clarify** — User types a request. Agent asks one quick clarifying question with a suggested default.
2. **Build** — Agent plans, generates code, and deploys. Live URL appears in ~10–20 seconds.
3. **Share** — Owner shares the link with a teammate, who gets an OTP-authenticated Viewer/Editor session — no separate signup.
4. **Edit** — Owner asks the agent (in chat) to add a feature. App redeploys to the same URL.
5. **Backtrack** — Owner opens the Decision Timeline, inspects each step the agent took, and reverts to a prior working version if the latest edit caused an issue.

---

## 8. Judging Criteria Alignment

| Criteria | How this project addresses it |
|---|---|
| **Problem & Impact** | Solves a real, recurring gap between "AI can generate an app" and "a non-technical person can actually use and share it" |
| **Agentic Depth** | Clarify-then-build reasoning, multi-step ReAct planning, tool use, self-correction via retries — all inspectable in the Decision Timeline |
| **Technical Execution** | Real multi-service AWS architecture (Bedrock, Fargate/Lambda, Cognito, DynamoDB, ALB/API Gateway), not a single API wrapper |
| **Ship It** | Fully deployed, live, reachable URL running on AWS infrastructure |

---

## 9. Setup & Local Development

```bash
# Clone the repo
git clone <repo-url>
cd <repo-name>

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Infra (deploy platform to AWS)
cd infra
cdk bootstrap
cdk deploy
```

### Environment Variables

```
AWS_REGION=
BEDROCK_MODEL_ID=
COGNITO_USER_POOL_ID=
COGNITO_APP_CLIENT_ID=
DYNAMODB_TABLE_NAME=
SES_SENDER_EMAIL=
```

---

## 10. Roadmap / Future Work

- Branching timeline diffs (visual compare between any two nodes, not just linear revert)
- Team-level shared workspaces (multiple apps under one organization)
- Support for stateful multi-user apps beyond simple forms/trackers
- Anomaly detection on agent traces (flag unusually costly or slow steps automatically)
- Marketplace of reusable "SmallOps" templates

---

## 11. Team

- [Add team member names / roles]

---

## 12. License

[Add license]

## Running the Application Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS Account (for Cognito, DynamoDB, S3)
- Gemini API Key

### Configuration (`.env`)
Create a `.env` file in the **root** of the project (`BharatBuilds/.env`) and add the following keys. 
*Note: The system requires `gemini-2.5-flash` or higher to bypass free-tier rate limits.*
```env
# AWS
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_ID=gemini-2.5-flash

# DynamoDB
DYNAMODB_TABLE_NAME=bharatbuilds-table

# Cognito
COGNITO_USER_POOL_ID=your_user_pool_id
COGNITO_APP_CLIENT_ID=your_client_id

# Lambda deploy target (Optional)
DEPLOY_LAMBDA_FUNCTION_NAME=bharatbuilds-deploy-runner
```

### Backend Setup
1. From the project root, create and activate a virtual environment:
   ```bash
   python -m venv backend/.venv
   source backend/.venv/bin/activate  # On Windows: backend\.venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the backend server from the **project root**:
   ```bash
   export PYTHONPATH=. 
   uvicorn backend.main:app --port 8000
   ```
   The backend will be available at `http://localhost:8000`.

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the `frontend` directory with your Cognito details (Vite needs these exposed):
   ```env
   VITE_COGNITO_USER_POOL_ID=your_user_pool_id
   VITE_COGNITO_APP_CLIENT_ID=your_client_id
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   The frontend will be accessible at **`http://localhost:3000`**. *(Note: API calls are automatically proxied to port 8000).*

### Application Features
- **Authentication**: You must register an account and verify your email via the OTP sent by AWS Cognito before you can access the builder.
- **Smart Deployment fallback**: If your AWS IAM User does not have `lambda:UpdateFunctionCode` permissions, the backend will gracefully bypass AWS Lambda and directly serve your generated HTML applications inline via the `/apps/{app_id}/live` route! 
- **Isolated Viewer**: Deployed apps run in an isolated iframe. You can also click the "Open in New Tab" icon to use them fully standalone.
