# Architecture

> Diagram and service mapping for the BharatBuilds platform.

See the architecture diagram in [README.md](../README.md#4-architecture).

## Service Mapping

| Layer | Service | Purpose |
|---|---|---|
| Agent / codegen | Amazon Bedrock | Clarify pass, planning, code generation, live edits |
| App runtime | AWS Fargate (ECS) | Isolated sandbox per deployed app |
| Fast-path runtime | AWS Lambda + Function URLs | Near-instant deploy for lightweight apps |
| Routing | ALB / API Gateway | Per-app path-based routing |
| Auth & sharing | Amazon Cognito | Magic link/OTP login, role-based access |
| Invites | Amazon SES | Email invitations |
| Data store | Amazon DynamoDB | App metadata, timeline, code snapshots |
| Static hosting | Amazon S3 + CloudFront | Dashboard frontend, static assets |
| Infra-as-code | AWS CDK | Reproducible platform deployment |
