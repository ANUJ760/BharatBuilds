# smallOps
> A cloud for small software: turn plain-language prompts into live, authenticated, shareable web applications deployed on AWS infrastructure, with a visual decision timeline, deterministic rollback, and autonomous self-healing maintenance.

Built for **Bharat Builds Tour 2026 (First Commit)** by WeMakeDevs × AWS.

---

## 1. The Problem

AI models can write working code from a prompt in seconds: a form, a tracker, a dashboard, or a lightweight internal tool. However, turning generated code into software that a team can reliably use still requires:

- Cloud provisioning and DevOps knowledge to deploy and expose live URLs
- Setting up authentication, user pools, and login flows
- Provisioning databases or object storage for application state
- Distributing access securely without sending raw source archives
- Safe maintenance and bug repair that will not silently break previously working features

Traditional cloud platforms are built for large-scale enterprise systems, introducing significant setup complexity. Most AI-generated applications are small software: single-purpose tools built for an individual or small team that must be deployed, shared, and maintained with zero friction.

TBD provides a dedicated, opinionated cloud platform designed specifically for small software, running natively on AWS.

---

## 2. Core Architecture and Capabilities

1. **Clarify-Then-Build**: Checks the prompt for structural ambiguities before generating code, asking up to 3 focused questions with default recommendations.
2. **Instant Deployment**: Deploys isolated container or serverless workloads to live, HTTPS-enabled AWS URLs in seconds.
3. **Zero-Config Auth and Sharing**: Wraps every deployed app in role-based authentication (Viewer and Editor) via magic links and OTP, without modifying the generated application logic.
4. **Decision Timeline and Deterministic Revert**: Records every plan, tool invocation, code diff, and deployment state in an interactive tree graph, enabling one-click rollback to any historical snapshot.
5. **Autonomous Maintenance**: Detects application errors and health degradation, diagnoses root causes with Amazon Bedrock, verifies candidate repairs locally in isolation, and enforces safety guards before any code is promoted.

---

## 3. Detailed Feature Breakdown

### 3.1 Prompt-to-App Generation
- Accepts natural language descriptions through a clean chat interface.
- Deconstructs requirements into a structured specification and generates complete, runnable Python/FastAPI or static frontend applications.
- Powered by Amazon Bedrock foundation models with strict schema validation.

### 3.2 Clarify-Then-Build
- Before generating code, an ambiguity detection step evaluates whether the prompt has missing data schemas, unclear role distinctions, or conflicting requirements.
- If ambiguities exist, the system prompts the user with up to 3 targeted multiple-choice questions with preselected defaults.
- Once answered or confirmed, code generation executes deterministically without conversational loops.
- Clarification questions and user choices are recorded as the root node of the Decision Timeline.

### 3.3 Instant AWS Deployment
- Applications are deployed to live, isolated AWS endpoints within 10 to 20 seconds.
- Execution options include:
  - **Fast-path runtime**: AWS Lambda functions paired with Function URLs for lightweight single-file applications.
  - **Container runtime**: AWS Fargate (ECS) tasks behind an Application Load Balancer for multi-file or stateful applications.
- Zero manual cloud configuration or infrastructure provisioning required by the end user.

### 3.4 Zero-Config Sharing and Role-Based Auth
- Every deployed app is secured out of the box using Amazon Cognito.
- Application owners can invite team members via email using Amazon SES.
- Collaborators authenticate via passwordless magic links or OTP tokens.
- Role enforcement:
  - **Viewer**: Read-only access to the running application.
  - **Editor**: Ability to submit modification prompts, inspect the decision timeline, trigger reverts, and request maintenance.

### 3.5 Decision Timeline and One-Click Revert
- Every agent action (clarification, planning, code generation, linting, deployment, maintenance) is logged as an immutable node in Amazon DynamoDB.
- Visualized as a connected graph where successful paths form the main trunk, while retries and maintenance repairs branch off cleanly.
- Node inspection panel provides:
  - Input prompt and system context
  - LLM reasoning and execution plan
  - Unified code diffs
  - Execution latency and token usage metrics
  - Node status (SUCCESS, ERROR, REVERTED)
- **Deterministic Revert**: Instantly rolls back the live AWS deployment to the exact code snapshot stored at any previous node without re-prompting.

### 3.6 Continuous Live Editing
- Users can request incremental changes in natural language ("add CSV export", "filter by date range").
- The agent computes localized diffs against the latest code snapshot and redeploys to the same stable URL.
- Each modification creates a new timeline node, maintaining a complete audit trail.

### 3.7 Autonomous Maintenance and Self-Healing
- **Health Probing**: Async synthetic HTTP health monitor tests endpoints for status codes, latency spikes, and connection failures.
- **Root-Cause Diagnosis and Repair**: Ingests error logs, stack traces, and existing code snapshots to produce targeted code patches via Amazon Bedrock.
- **Candidate Verification**: Compiles candidate code in an isolated environment, verifies syntax, imports the handler, and runs smoke executions to guarantee functional validity before deployment.
- **Safety Guards**:
  - Max 2 repair attempts per maintenance job to prevent looping.
  - Concurrency lock per application to prevent overlapping maintenance runs.
  - Prompt sanitization to strip injection payloads from untrusted stack traces.
  - Configuration guardrails rejecting unauthorized modifications to authentication, environment settings, or infrastructure.

---

## 4. System Architecture

```
                        +-------------------------+
                        |   Dashboard (Frontend)  |
                        |   S3 + CloudFront       |
                        +------------+------------+
                                     |
                         +-----------v------------+
                         |   API Layer            |
                         |   API Gateway + Lambda |
                         +-----------+------------+
                                     |
        +----------------------------+-----------------------------+
        |                            |                             |
+-------v--------+          +--------v----------+         +--------v--------+
|  Agent Layer   |          |  Deploy Layer     |         |  Auth Layer     |
|  Amazon Bedrock|          |  AWS Fargate (ECS)|         |  Amazon Cognito |
|  - Clarify     |          |  or Lambda        |         |  - Magic links  |
|  - Codegen     |          |  Function URLs    |         |  - OTP login    |
|  - Maintenance |          |  ALB / API GW     |         |  - Roles        |
+-------+--------+          +--------+----------+         +--------+--------+
        |                            |                             |
        +----------------------------+-----------------------------+
                                     |
                        +------------v------------+
                        |  Data Layer             |
                        |  DynamoDB               |
                        |  - App metadata         |
                        |  - Timeline step graphs |
                        |  - Code snapshots       |
                        |  S3 (Asset storage)     |
                        +-------------------------+
```

### AWS Services Map

| Layer | Service | Purpose |
|---|---|---|
| AI and Orchestration | **Amazon Bedrock** | Ambiguity clarification, planning, code generation, and error diagnosis |
| App Runtime (Fast Path) | **AWS Lambda + Function URLs** | Sub-second cold starts and rapid deployment for lightweight applications |
| App Runtime (Container) | **AWS Fargate (ECS)** | Isolated container environments for complex applications |
| Routing and Gateway | **Application Load Balancer / API Gateway** | Public routing, SSL termination, and path-based dispatch |
| Authentication | **Amazon Cognito** | Passwordless user authentication, JWT session verification, and role assignments |
| Notifications and Invites | **Amazon SES** | Secure email dispatch for workspace invites and magic links |
| Persistence | **Amazon DynamoDB** | Single-table storage for applications, decision traces, snapshots, and maintenance state |
| Static Hosting | **Amazon S3 + CloudFront** | Global CDN distribution for dashboard assets and generated frontends |
| Infrastructure as Code | **AWS CDK** | Fully reproducible TypeScript CDK stacks for all cloud resources |

---

## 5. Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, React Flow (interactive timeline graph), Vite
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, Boto3, HTTPX
- **Agent and Repair Engine**: Amazon Bedrock Converse API, AST-based candidate verifiers, strict prompt guardrails
- **Database**: Amazon DynamoDB (single-table access patterns with composite keys)
- **Infrastructure**: AWS Cloud Development Kit (CDK) in TypeScript

---

## 6. Repository Structure

```
.
├── backend/
│   ├── main.py                         # FastAPI application entrypoint
│   ├── config.py                       # Environment configuration and settings
│   ├── logger.py                       # Structured logging configuration
│   ├── agent/
│   │   ├── clarify.py                  # Ambiguity detection and structured questions
│   │   ├── planner.py                  # Multi-step planning and ReAct execution loop
│   │   ├── codegen.py                  # Code generation and patch formatting
│   │   ├── repair.py                   # Bedrock-backed diagnosis and repair engine
│   │   ├── candidate_verifier.py       # Isolated AST and runtime candidate verification
│   │   ├── health_probe.py             # Async synthetic HTTP health monitoring
│   │   ├── safety_guards.py            # Concurrency, sanitization, and security guardrails
│   │   ├── maintenance_orchestrator.py # End-to-end self-healing orchestrator
│   │   ├── bedrock_client.py           # Amazon Bedrock client abstraction
│   │   └── trace_logger.py             # Timeline node recorder for DynamoDB
│   ├── api/
│   │   ├── routes_apps.py              # Application lifecycle and management endpoints
│   │   ├── routes_timeline.py          # Timeline retrieval and deterministic revert endpoints
│   │   ├── routes_share.py             # Invitations, magic links, and role management
│   │   ├── routes_deploy.py            # Deployment triggers and status polling
│   │   └── routes_maintenance.py       # Maintenance issue intake and repair execution
│   ├── auth/
│   │   ├── cognito_client.py           # Amazon Cognito authentication handlers
│   │   └── roles.py                    # Viewer and Editor permission checks
│   ├── deploy/
│   │   ├── lambda_deployer.py          # AWS Lambda fast-path deployment engine
│   │   ├── fargate_deployer.py         # AWS Fargate container deployment engine
│   │   └── router.py                   # Dynamic route assignment
│   ├── models/
│   │   ├── app.py                      # Core Pydantic schemas (App, Maintenance, Verification)
│   │   └── timeline.py                 # Decision timeline node schemas
│   ├── storage/
│   │   ├── dynamodb_client.py          # DynamoDB single-table persistence
│   │   └── s3_client.py                # S3 artifact and snapshot storage
│   ├── tests/                          # Comprehensive unit and integration test suite
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                    # React application entrypoint
│   │   ├── App.tsx                     # Top-level routing and state providers
│   │   ├── api/                        # Typed backend API client
│   │   ├── components/
│   │   │   ├── ui/                     # Design system primitives (buttons, inputs, modals)
│   │   │   ├── chat/                   # Prompt submission and clarification chips
│   │   │   ├── timeline/               # Decision timeline graph (React Flow) and inspector
│   │   │   ├── dashboard/              # App cards, deployment indicators, share dialogs
│   │   │   └── layout/                 # Navigation bars, headers, page shells
│   │   ├── pages/
│   │   │   ├── Home.tsx                # Prompt input and clarification page
│   │   │   ├── AppView.tsx             # Live application viewer, sharing, and edit panel
│   │   │   ├── Dashboard.tsx           # User application inventory
│   │   │   ├── Timeline.tsx            # Full-screen decision tree graph and rollback UI
│   │   │   └── Auth.tsx                # Authentication and magic link verification
│   │   └── design/
│   │       ├── tokens.css              # Design tokens (colors, spacing, elevations)
│   │       ├── typography.css          # Typography scales
│   │       └── motion.css              # Isolated animation utilities
│   ├── package.json
│   └── vite.config.ts
│
├── infra/                              # AWS CDK infrastructure definition
│   ├── bin/
│   │   └── app.ts                      # CDK application entrypoint
│   ├── lib/
│   │   ├── network-stack.ts            # VPC, subnets, and security groups
│   │   ├── compute-stack.ts            # ECS cluster, task definitions, Lambda handlers
│   │   ├── data-stack.ts               # DynamoDB tables and S3 buckets
│   │   ├── auth-stack.ts               # Cognito user pools and clients
│   │   └── frontend-stack.ts           # S3 hosting and CloudFront distribution
│   ├── cdk.json
│   └── package.json
│
└── generated-app-runtime/              # Base sandbox container runtime for generated apps
    └── Dockerfile
```

---

## 7. Operational Workflow

### 7.1 Creation and Deployment
1. **Prompt Intake**: The user submits a natural language app request.
2. **Ambiguity Clarification**: The agent identifies underspecified requirements and requests targeted choices with recommended defaults.
3. **Plan and Codegen**: The agent creates an execution plan, generates structured application code, and validates imports.
4. **Deploy**: The code is packaged and deployed to an isolated AWS Lambda or Fargate endpoint.
5. **Timeline Logging**: All steps, rationale, and the initial code snapshot are committed to DynamoDB.

### 7.2 Sharing and Collaboration
1. **Invite**: The app owner invites collaborators by email.
2. **Session**: Collaborators receive an SES-dispatched link and authenticate via Cognito OTP.
3. **Role Enforcement**: Viewers access the application UI; Editors can submit modification requests and manage rollbacks.

### 7.3 Iterative Editing and Reversion
1. **Chat Updates**: The owner requests updates; the agent generates a patch and redeploys to the same URL.
2. **Audit and Rollback**: If a change causes unexpected behavior, the user opens the timeline, selects a prior verified node, and triggers a deterministic rollback.

### 7.4 Auto-Maintenance Pipeline
```
[Issue Detected / Submitted]
             |
             v
[Safety Guards Check] ---> (Reject if invalid/unsafe/exceeded attempts)
             |
             v
[Bedrock Diagnosis & Repair]
             |
             v
[Candidate Verification (Local AST + Import + Smoke Exec)]
             |
      +------+------+
      |             |
   (Passed)      (Failed)
      |             |
      v             v
[Stage Candidate] [Retry Repair (Max 2 Attempts)]
```

---

## 8. Safety and Reliability Controls

- **Per-Job Attempt Budget**: Strictly enforces a maximum of 2 repair attempts per maintenance job to eliminate infinite loops.
- **Concurrency Locks**: Prevents overlapping maintenance jobs from executing against the same application.
- **Input Sanitization**: Cleans untrusted stack traces, error outputs, and issue descriptions before embedding them in LLM prompts to prevent prompt injection.
- **Configuration Protection**: Rejects patches attempting to modify system-level configurations, authentication mechanisms, or cloud infrastructure.
- **Pre-Deployment Isolation**: All candidate code must pass AST compilation, handler extraction, and isolated execution tests before deployment is initiated.

---

## 9. Getting Started

### Prerequisites
- Python 3.12+ (3.12 is required for `moto` AWS mocking to work flawlessly in tests)
- Node.js 20+ and npm
- AWS Account (for Cognito, DynamoDB, S3)
- Google Gemini API Key (Optional, but highly recommended as fallback)

### 9.1 Configuration (`.env`)
Create a `.env` file in the **root** of the project (`BharatBuilds/.env`) and add the following keys. 

```env
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Amazon Bedrock (Primary LLM - Optional if using Gemini)
BEDROCK_MODEL_ID=deepseek.v3-1

# Google Gemini API (Fallback LLM)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_ID=gemini-2.5-flash

# DynamoDB
DYNAMODB_TABLE_NAME=bharatbuilds-table

# Cognito
COGNITO_USER_POOL_ID=your_user_pool_id
COGNITO_APP_CLIENT_ID=your_client_id

# S3 & Deployment
S3_ASSETS_BUCKET=bharatbuilds-assets
DEPLOY_LAMBDA_FUNCTION_NAME=bharatbuilds-deploy-runner
```

*Note: The backend features an intelligent **Dual-LLM** pipeline. It attempts AWS Bedrock first if `BEDROCK_MODEL_ID` is set and credentials are valid. If rate limits, permission boundaries, or invalid keys cause a failure, it seamlessly falls back to the Google Gemini API.*

### 9.2 Backend Setup
From the project root:

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Run backend test suite (fully covered with mocked AWS services)
export PYTHONPATH=.
pytest backend/

# Start local API server
export PYTHONPATH=.
uvicorn backend.main:app --port 8000
```
The backend will be available at `http://localhost:8000`.

### 9.3 Frontend Setup
In a new terminal:

```bash
cd frontend
npm install

# Set Vite environment variables inside frontend/.env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
echo "VITE_COGNITO_USER_POOL_ID=your_user_pool_id" >> .env
echo "VITE_COGNITO_APP_CLIENT_ID=your_client_id" >> .env

# Start frontend dev server
npm run dev
```
The frontend will be available at `http://localhost:3000`.

---

## 10. Intelligent Deployments & Fallbacks

- **AWS IAM Graceful Bypass**: If your AWS IAM User does not have `lambda:UpdateFunctionCode` permissions (or if deployment fails for any reason), the backend gracefully bypasses AWS Lambda and serves your generated applications directly via the `/apps/{app_id}/live` FastAPI route.
- **Dual-LLM Routing**: Enjoy the reliability of Bedrock with the flexibility of Gemini. Ensure at least one set of keys is provided.

---

## 11. Testing and CI/CD

A fully automated **GitHub Actions CI/CD Pipeline** is integrated into `.github/workflows/ci.yml`. On every push to `main`:
1. It provisions **Python 3.12** and runs all `125` robust backend Pytest suites (with auto-mocked AWS environments).
2. It provisions **Node 20**, installs UI dependencies, and executes `npm run build` to type-check `tsc` and Vite-compile the React frontend.

To run tests locally:
```bash
source backend/.venv/bin/activate
export PYTHONPATH=.
pytest backend/
```

---

## 12. License

This project is licensed under the MIT License.
