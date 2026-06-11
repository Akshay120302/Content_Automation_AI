# Content Automation AI

This repository implements a content automation platform that orchestrates AI agents to generate, assemble, validate, and publish content across social platforms. It is split into a **backend** (FastAPI + Celery) and a **frontend** (Vite/React). The system is designed for production-ready workflows — async job execution, asset management (S3), database-backed pipelines, and modular agents.

This README is written for recruiters and reviewers: it explains what the project contains today, what's missing, how to run it locally, and the long-term product vision.

**Repository layout**
- **Backend:** [server/main.py](server/main.py) — FastAPI entrypoint, app modules under [server/app](server/app)
- **Frontend:** [client/src/main.jsx](client/src/main.jsx) — React + Tailwind UI, components under [client/src/components](client/src/components)
- **Migrations:** [alembic/](alembic) — database migrations
- **Docs & Guides:** [server/PROJECT_INFO.md](server/PROJECT_INFO.md), [QUICK_START.md](QUICK_START.md)

**High-level summary**
- **Orchestration:** DAG-based orchestrator and state-machine coordinate multi-step pipelines (see [server/app/orchestration](server/app/orchestration)).
- **Agents:** Modular agents (content, composer, quality, video providers) live under [server/app/agents](server/app/agents).
- **Async execution:** Celery + Redis workers configured in [server/app/celery_config](server/app/celery_config).
- **Storage:** Files are uploaded directly to S3 (presigned URLs) with metadata stored in `pipeline_assets`. See [server/app/models/pipeline.py](server/app/models/pipeline.py).
- **Database:** Postgres with Alembic migrations under [server/alembic/versions](server/alembic/versions).

**What is implemented (current)**
- **Pipeline model and assets:** `pipelines`, `pipeline_assets`, `pipeline_runs`, and supporting models are present. See [server/app/models/pipeline.py](server/app/models/pipeline.py) and [server/alembic/versions/e7f8a9b0c1d2_add_pipeline_assets_table.py](server/alembic/versions/e7f8a9b0c1d2_add_pipeline_assets_table.py).
- **Orchestration primitives:** DAG and state machine implementation under [server/app/orchestration](server/app/orchestration).
- **Agents & video providers:** Agents for content, composer, and video providers are scaffolded under [server/app/agents](server/app/agents) (including ComfyUI / Replicate / Runway providers).
- **Celery tasks & scheduling:** Task definitions and the Celery app exist under [server/app/celery_config](server/app/celery_config).
- **Frontend UI:** React components for pipeline creation and pages are in [client/src/components](client/src/components). Core app entry is [client/src/App.jsx](client/src/App.jsx).
- **Auth & users:** User model, JWT/refresh token handling, and OAuth account scaffolding exist under [server/app/models/user.py](server/app/models/user.py).
- **Social module scaffold (new):** A `social` package was added (`server/app/social`) including SQLAlchemy models and an Alembic migration to add `social_accounts` and `social_posts`. A Fernet-based token encryption util exists as an MVP at [server/app/social/token_service.py](server/app/social/token_service.py).

**Database tables added by this project**
- **pipelines** — pipeline configuration and schedule ([server/app/models/pipeline.py](server/app/models/pipeline.py)).
- **pipeline_assets** — metadata for uploaded assets ([server/alembic/versions/e7f8a9b0c1d2_add_pipeline_assets_table.py](server/alembic/versions/e7f8a9b0c1d2_add_pipeline_assets_table.py)).
- **pipeline_runs / pipeline_run_steps / pipeline_events** — execution tracking ([server/app/models/execution.py](server/app/models/execution.py)).
- **social_accounts / social_posts** — social integration tables scaffolded and migration added at [server/alembic/versions/a1b2c3d4e5f6_add_social_tables.py](server/alembic/versions/a1b2c3d4e5f6_add_social_tables.py).

**What still needs to be implemented (high priority for a working MVP)**
The following list is ordered for a minimal, secure MVP that can connect accounts and post content.

- **OAuth 2.0 flow (server-side):** implement redirect and callback endpoints, state validation, and code→token exchange for each platform. Start with Instagram (Meta Graph API), YouTube, and LinkedIn. (Files to add: `server/app/social/oauth_service.py`, `server/routes/social_routes.py`)
- **Token encryption & refresh:** production-grade key management (AWS KMS) integration and automated refresh of expired tokens. Current Fernet util is MVP only (`server/app/social/token_service.py`).
- **Platform adapters (Posting):** implement `PostingService` and adapters: `InstagramAdapter`, `YouTubeAdapter`, `LinkedInAdapter` to handle uploads, polling, and publish flows. Place under `server/app/social/adapters/`.
- **Celery posting tasks:** create async Celery tasks that the orchestrator invokes to post artifacts, handle 429s, expiries, retries, and backoff. Integrate with `social_posts` to record results.
- **Webhook endpoints:** `/webhooks/{platform}` to accept signature-verified callbacks (processing status, revocations, etc.).
- **Frontend "Connect social account" UI:** Add UI to redirect users to OAuth flows and show connected accounts in profile/dashboard (client-side changes under [client/src/components](client/src/components)).
- **Credential management & UX:** OAuth consent, scope selection, and token refresh UX.
- **Large media flow:** implement S3-based storage and presigned URL uploads for videos, then use platform resumable upload or direct-to-provider signed URLs without proxying through the server.
- **Testing & monitoring:** E2E tests around OAuth, upload, posting; structured logging and metrics for posting failures and rate-limits.

**Security & production hardening tasks**
- Replace Fernet with AWS KMS or equivalent key vault for token encryption and key rotation.
- Ensure tokens are never logged and that DB backups protect encrypted tokens.
- Validate `redirect_uri` and `state` on OAuth flows to prevent CSRF.
- Enforce minimal scopes when requesting platform permissions.

**Developer setup & run (local)**
1. Install backend dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # or on Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r server/requirements.txt
```

2. Add required environment variables (example)

```bash
export DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/content_ai"
export REDIS_URL="redis://localhost:6379/0"
export SOCIAL_TOKEN_ENCRYPTION_KEY="<FERNET_KEY_HERE>"
# Add any platform client IDs/secrets for OAuth when implementing
```

3. Run DB migrations

```bash
cd server
alembic upgrade head
```

4. Start backend API

```bash
uvicorn server.main:app --reload --port 8000
```

5. Start Celery worker (in separate terminal)

```bash
cd server
celery -A app.celery_config.celery_app.app worker --loglevel=info
```

6. Start frontend

```bash
cd client
npm install
npm run dev
```

**How the social posting flow is intended to work (MVP)**
1. User clicks **Connect Account** in the dashboard → frontend redirects to backend endpoint that starts OAuth (server route verifies `state` and returns platform OAuth URL).
2. User approves and platform redirects to backend callback → backend exchanges code for tokens, encrypts them, and writes a `social_accounts` record.
3. When a pipeline run produces a final artifact (video/image/text), the orchestrator enqueues a Celery posting task pointing to `pipeline_runs.run_id` and target `social_account_id`.
4. `PostingService` picks the correct adapter, uploads media (using presigned S3 URLs for large files), polls the platform if needed, and marks `social_posts` as `posted` or `failed`.
5. Platform webhook events (optional) update status and surface errors or revocations.

**Vision (final product)**
The final product is a reliable content automation platform where creators and teams can define repeatable pipelines that: generate multimedia content, quality-check it, schedule posts to multiple social platforms, and provide an auditable run log and retry behavior. Key production attributes:

- **Secure credential management** (KMS + vaults)
- **Modular platform adapters** that encapsulate platform-specific upload and publishing logic
- **Async posting** with retries, exponential backoff and bounded retry limits
- **Scalable media handling** (direct-to-S3 uploads, resumable provider uploads)
- **Observability** (structured logs, events, dashboards for runs and social posts)

**How you can help / next steps I can take for you**
- Implement Instagram OAuth endpoints and adapter (recommended first MVP). I can implement this end-to-end: routes, controller, adapter, and a frontend Connect button.
- Replace the local Fernet encryption with an AWS KMS integration and key rotation flow.
- Implement Celery posting tasks and example adapters for Instagram/YouTube/LinkedIn.

If you'd like, tell me which platform to prioritize (Instagram, YouTube, or LinkedIn) and I will implement the OAuth callback, token storage, and a working adapter for that platform next.

---
Maintainers: check [server/PROJECT_INFO.md](server/PROJECT_INFO.md) for project-specific notes and deployment hints.
