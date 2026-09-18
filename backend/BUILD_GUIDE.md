# Backend Build Guide (For AI Coding Agents)

This guide is written to be handed directly to an AI coding agent (e.g. Claude Code) as its operating instructions for building the `backend/` portion of this project. It assumes the agent has shell access, git, and Python toolchains available.

**Status note:** infra for this build was provisioned **manually through the AWS Console**, not via CDK — the local AWS CLI wasn't cooperating during setup, so Commits 3–6 (originally CDK stacks) were replaced with a one-time manual console setup, already completed. See Section 1a for exactly what exists and Section 4 for the resulting `.env` values. The agent does not need to run `cdk` commands and should not attempt to create these resources — only read their names/IDs from `.env` and use them via `boto3`.

**Golden rules for the agent:**
1. Work in the commit order below. Do not skip ahead — each commit assumes the previous one is working.
2. After every commit, run the listed verification command(s) before moving on. If a command fails, fix it before committing.
3. Never commit real credentials, `.env` files, or AWS account IDs. Only commit `.env.example`.
4. Keep commits scoped to exactly what's listed — small, reviewable, revertable steps, not one giant dump.
5. AWS resources (DynamoDB table, S3 bucket, Cognito pool, Lambda function) already exist — see Section 1a. Read their names from `.env`, never try to create/recreate them.
6. `boto3` reads credentials from `~/.aws/credentials` / `~/.aws/config` — these were set up manually (not via `aws configure`, since the CLI wasn't working locally) and don't require the `aws` CLI binary to function at all.

---

## 1. Prerequisites Checklist (verify before Commit 1)

The agent should confirm these before starting, and stop to ask the human if any are missing:

- [ ] `git` initialized, remote configured
- [ ] Python 3.11+ and `pip` available
- [ ] `~/.aws/credentials` and `~/.aws/config` exist and contain a valid IAM user's access key + `region = ap-south-1` (set up manually — see Section 3; the `aws` CLI binary itself does not need to work, `boto3` only needs these two files)
- [ ] A `.env.example` file exists at the repo root (create in Commit 1 if not)
- [ ] A `.env` file (gitignored) exists with the real values from Section 4, matching the AWS resources already created manually in the console

## 1a. AWS Resources Already Provisioned (manual console setup — do not recreate)

| Resource | How it was created | Where its ID/name goes |
|---|---|---|
| DynamoDB table (`app_id` PK, `step_id` SK, on-demand) | Manually, DynamoDB Console | `DYNAMODB_TABLE_NAME` |
| S3 bucket (private, versioned) | Manually, S3 Console | `S3_ASSETS_BUCKET` |
| Cognito User Pool (email sign-in, no MFA) + App Client | Manually, Cognito Console — **created under the root account** (IAM user hit permissions issues navigating the console's Identity Pools flow by mistake; User Pool creation itself only needs `cognito-idp:CreateUserPool`, already in the IAM policy, so this was root-only for the one creation step) | `COGNITO_USER_POOL_ID`, `COGNITO_APP_CLIENT_ID` |
| Lambda function + Function URL (fast-path deploy target) | Manually, Lambda Console | `DEPLOY_LAMBDA_FUNCTION_NAME` |

If any of these four don't exist yet, create them manually before starting Commit 1 — the backend code from Commit 8 onward assumes they're already there.

---

## 2. Commit Plan (18 commits)

Each entry: **goal → files touched → commands to run → acceptance check → commit message**. Run tests/checks after each step; only commit on green.

### Phase 0 — Scaffolding

**Commit 1: Repo and tooling scaffold**
- Create `backend/`, `infra/`, `docs/` directories per the folder structure in `README.md`.
- Add `backend/requirements.txt` (fastapi, uvicorn, boto3, pydantic, python-dotenv, pytest, httpx).
- Add `backend/main.py` with a bare FastAPI app and a `/health` route returning `{"status": "ok"}`.
- Add `.env.example` with all variables from Section 4 below (empty values).
- Add `.gitignore` (`.env`, `__pycache__/`, `node_modules/`, `cdk.out/`, `*.pyc`).
- **Verify:** `uvicorn backend.main:app --reload` starts; `curl localhost:8000/health` returns 200.
- **Commit message:** `chore: scaffold backend project structure and health endpoint`

**Commit 2: Config loader and settings module**
- Add `backend/config.py` using `pydantic-settings` (or `python-dotenv` + a `Settings` class) to load every env var from Section 4, with clear validation errors if a required one is missing.
- Wire `/health` to also report which config values are present (booleans only — never echo secret values).
- **Verify:** running with a missing required var raises a clear startup error, not a silent `None`.
- **Commit message:** `feat: add centralized settings loader with env validation`

### Phase 1 — Infrastructure

Originally planned as CDK stacks (Commits 3–6). **Skipped** — the four AWS resources were created manually through the console instead (see Section 1a), since the local AWS CLI wasn't cooperating and CDK requires it. Nothing for the agent to do here; proceed straight to Phase 2 once `.env` is filled in with the real resource names/IDs.

If you later get the CLI working and want to migrate to CDK for reproducibility (recommended once the hackathon pressure is off — hand-created resources are harder to tear down cleanly and easy to forget about after judging), that would slot back in here as its own set of commits, importing the existing resources rather than creating new ones (`cdk import` or manually writing `CfnTable`/`CfnUserPool` constructs that reference the existing physical resource IDs).

### Phase 2 — Backend Core

**Commit 7: Pydantic models**
- Add `backend/models/` with schemas: `App`, `TimelineStep`, `Invite`, `ClarifyQuestion`, `ClarifyResponse`.
- **Verify:** `pytest backend/tests/test_models.py` (write 2–3 basic instantiation/validation tests).
- **Commit message:** `feat: add core Pydantic data models`

**Commit 8: DynamoDB client wrapper**
- Add `backend/storage/dynamodb_client.py`: `put_item`, `get_item`, `query_by_app_id` helper functions using `boto3`, reading the table name from `config.py`.
- Add `backend/storage/s3_client.py`: `upload_asset`, `get_asset_url`.
- **Verify:** unit tests using `moto` (mocked AWS) for both clients — no real AWS calls in tests.
- **Commit message:** `feat: add DynamoDB and S3 storage clients with mocked tests`

**Commit 9: Bedrock client wrapper**
- Add `backend/agent/bedrock_client.py`: a thin wrapper around `boto3`'s `bedrock-runtime` `invoke_model`, with retry/backoff and a helper for forcing structured JSON output.
- **Verify:** unit test with a mocked Bedrock response; confirm the wrapper parses both plain-text and JSON-mode responses correctly.
- **Commit message:** `feat: add Bedrock client wrapper with structured-output support`

**Commit 10: Clarify-then-build pass**
- Add `backend/agent/clarify.py`: takes a raw prompt, calls Bedrock with the ambiguity-check system prompt, returns `ClarifyResponse` (0–3 questions, each with a suggested default and `why_it_matters`).
- Add `POST /apps/clarify` route.
- **Verify:** unit test with a mocked Bedrock call returning a fixture JSON payload; confirm the route returns a well-formed response for both the "no questions" and "3 questions" cases.
- **Commit message:** `feat: add clarify-then-build ambiguity check pass`

**Commit 11: ReAct planner and codegen**
- Add `backend/agent/planner.py`: the hand-rolled ReAct loop (plan → tool call → codegen → retry-on-error), calling `bedrock_client.py`.
- Add `backend/agent/codegen.py`: takes a resolved prompt (+ clarify answers) and produces app source code as a string/file bundle.
- **Verify:** unit test with mocked Bedrock responses simulating one retry; confirm the loop terminates and returns valid code + a full step trace list.
- **Commit message:** `feat: add ReAct planner and code generation step`

**Commit 12: Trace logger and timeline endpoints**
- Add `backend/agent/trace_logger.py`: writes every step from the planner (plan/tool_call/codegen/retry) into DynamoDB as a `TimelineStep`.
- Add `backend/api/routes_timeline.py`: `GET /apps/{id}/timeline`, `GET /apps/{id}/timeline/{step_id}`.
- **Verify:** integration test (with `moto`) that runs a mocked planner call and confirms the resulting DynamoDB query returns an ordered, parent-linked step tree.
- **Commit message:** `feat: add agent trace logging and timeline read endpoints`

**Commit 13: Deploy layer (Lambda fast path)**
- Add `backend/deploy/lambda_deployer.py`: packages generated code, deploys/updates it to the Lambda function created manually in Section 1a (via `update_function_code`), returns the live Function URL.
- Add `POST /apps/{id}/deploy`.
- **Verify:** integration test against the real Lambda function in `ap-south-1` OR mocked `boto3` Lambda client if you want a CI-safe test — mark clearly which mode ran.
- **Commit message:** `feat: add Lambda-based deploy step and deploy endpoint`

**Commit 14: Revert endpoint**
- Add `POST /apps/{id}/revert/{step_id}`: fetches the code snapshot stored at that step and re-runs `lambda_deployer.py` against it, logging the revert as a new timeline node with `status: reverted`.
- **Verify:** test that deploys version A, deploys version B, reverts to A, and confirms the live Function URL serves A's content again.
- **Commit message:** `feat: add revert-to-step endpoint`

**Commit 15: Auth and role enforcement**
- Add `backend/auth/cognito_client.py`: verify JWT from Cognito, extract user + group (Viewer/Editor).
- Add `backend/auth/roles.py`: a FastAPI dependency that blocks write routes (`deploy`, `revert`, `share`) for Viewer-role users.
- Wire the dependency into the relevant routes from Commits 13–14.
- **Verify:** test with a mocked Viewer token hitting `/deploy` → expect 403; Editor token → expect 200.
- **Commit message:** `feat: add Cognito auth verification and role-based access control`

**Commit 16: Sharing and invites**
- Add `backend/api/routes_share.py`: `POST /apps/{id}/invite` (email + role) using SES to send the invite link.
- **Verify:** unit test with a mocked SES client confirming the correct email params are sent; no real email sent in CI.
- **Commit message:** `feat: add app sharing and invite endpoint`

### Phase 3 — Hardening

**Commit 17: Error handling and structured logging**
- Add a global FastAPI exception handler returning consistent JSON error shapes (`{error, message, request_id}`).
- Add structured logging (`structlog` or stdlib `logging` with JSON formatter) across `agent/`, `deploy/`, and `api/` modules.
- **Verify:** trigger a deliberate error in a test (bad Bedrock response) and confirm the error shape and log line format.
- **Commit message:** `chore: add global error handling and structured logging`

**Commit 18: End-to-end smoke test + seed script**
- Add `backend/tests/test_e2e_smoke.py`: runs the full flow — clarify → codegen → deploy → timeline → revert — against mocked AWS clients, asserting each stage in sequence.
- Add `backend/scripts/seed_demo_app.py`: a one-command script that creates a demo app end-to-end, for use right before the live demo.
- **Verify:** `pytest backend/tests/test_e2e_smoke.py` passes; `python backend/scripts/seed_demo_app.py` produces a working demo app locally.
- **Commit message:** `test: add end-to-end smoke test and demo seed script`

---

## 3. Can This Be Built Agentically? What Needs Manual Setup

**Short answer: yes, all of Phase 2–3 (Commits 7–18, the actual backend logic) can be written and iterated on by an agent working through the commit plan unattended.** Infra creation turned out to need more manual, human-only steps than originally planned, because the local AWS CLI wasn't working — here's what actually had to happen by hand, in the order it happened:

### Done manually (console-only, no CLI)
1. **AWS account + billing** — $200 in credits applied, confirmed under Billing → Credits.
2. **IAM group + scoped policy** — `hackathon-builders` group created, with an inline policy covering Bedrock, DynamoDB, S3, Lambda, Cognito (`cognito-idp:*` only, not `cognito-identity:*`), SES, and a `PassRole` statement scoped to `arn:aws:iam::*:role/cdk-*` with an `iam:PassedToService` condition (fixed after an Access Analyzer warning flagged the original wildcard version).
3. **IAM user created**, added to the group, access key generated **via root** (the IAM user itself lacks `iam:CreateAccessKey` for itself or others by design — only root/an admin identity can do this under the current policy).
4. **`~/.aws/credentials` and `~/.aws/config` written by hand** (not via `aws configure`, since the CLI itself wasn't functioning locally) — `boto3` reads these two files directly and doesn't need the `aws` binary to work at all.
5. **Amazon Bedrock — DeepSeek model** — no manual access request needed. Unlike Anthropic models on Bedrock (which can prompt a one-time use-case form), DeepSeek is a fully-managed serverless model with no extra enablement step. Only available in a subset of regions — confirmed `ap-south-1` (Mumbai) is supported, so no cross-region latency tradeoff.
6. **DynamoDB table, S3 bucket, Lambda function + Function URL** — created directly in their respective consoles (see Section 1a), replacing what would have been CDK stacks.
7. **Cognito User Pool + App Client** — created **under root**, not the IAM user. Not a permissions gap in the policy for User Pools specifically (`cognito-idp:CreateUserPool` was already granted) — the issue was navigating into the wrong Cognito flow (**Identity Pools**, a different feature for federated AWS credentials) a couple of times first, which *does* require permissions the policy correctly doesn't grant (`cognito-identity:*`). Once on the correct User Pools flow, root was used simply to move fast rather than debug further. The pool itself is account-level, not tied to which identity created it — the IAM user can manage it going forward.
8. **AWS Builder Center profile + WeMakeDevs account** — required for hackathon eligibility itself; registered separately, not part of the AWS resource setup.

### Skipped entirely
- **CDK** — not used. No `cdk bootstrap`, no `cdk deploy`. All four resources exist as hand-created, standalone console resources. Revisit post-hackathon if reproducibility matters (see the note in Phase 1 above).
- **Amazon SES sender verification** — not yet done. Needed only before Commit 16 (invites) works for real; do this whenever you get to that commit, verifying the 2–3 specific email addresses you'll demo with.

### Safe to fully delegate to the agent
- Everything in Phase 2 (Commits 7–16) and Phase 3 (Commits 17–18) — pure Python, tests run against mocked AWS (`moto`) so no live account calls are needed except where a commit's verify step explicitly says to test against the real resources.
- Writing/updating `.env.example`, tests, and docs.

### Recommended sequencing from here
1. Fill in real values in `.env` from Section 1a's resources (done).
2. Agent: Commits 1–2 (no AWS needed yet).
3. Agent: Commits 7–18 in order, using `moto`-mocked tests by default, switching to real-resource integration tests only where a commit calls for it (9, 13, 14, 15).
4. Human: SES sender verification before Commit 16 actually needs to send mail.
5. Human: one final manual smoke test on the actual live Lambda Function URL before the demo — "passed in CI" and "works on stage in front of judges" can diverge, and this is the one step worth not delegating.

---

## 4. Environment Variables (`.env.example`)

```
# AWS
AWS_REGION=ap-south-1
AWS_PROFILE=default

# Bedrock — DeepSeek (not Anthropic; no use-case form needed)
BEDROCK_MODEL_ID=deepseek.v3-1

# DynamoDB
DYNAMODB_TABLE_NAME=

# S3
S3_ASSETS_BUCKET=

# Cognito
COGNITO_USER_POOL_ID=
COGNITO_APP_CLIENT_ID=

# SES
SES_SENDER_EMAIL=

# Lambda deploy target
DEPLOY_LAMBDA_FUNCTION_NAME=

# App
BACKEND_ENV=development
LOG_LEVEL=info
```

Never commit a populated `.env` — only `.env.example` (values blanked as above, region/model left as sensible defaults) — as set up in Commit 1. Confirm the exact `BEDROCK_MODEL_ID` string in the Bedrock console's Model catalog before wiring it into `bedrock_client.py` (Commit 9) — Bedrock model IDs are versioned and the exact string matters for `InvokeModel` calls.
