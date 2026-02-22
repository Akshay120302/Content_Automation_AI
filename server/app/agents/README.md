# Production-Grade Agentic Content Generation Platform

## Architecture Overview

This is a **production-grade**, **agentic content generation platform** built with:

- **Deterministic Execution Graphs (DAGs)** - Not simple prompt chaining
- **Bounded Retries** - No infinite loops
- **Parallel Agent Execution** - Optimized for performance
- **Comprehensive Observability** - Full audit trails
- **Quality Control** - Multi-stage validation
- **Failure Policies** - Graceful degradation
- **Auditable Logs** - Append-only event system
- **Restartable Workflows** - Resume from failure points

Think **Temporal / Airflow / Prefect** architecture, purpose-built for LLM + media agents.

---

## Core Components

### 1. Orchestration Agent (Central Brain)
**Location:** `server/app/orchestration/orchestration_agent.py`

**Control plane**, NOT a content generator.

**Responsibilities:**
- Load pipeline configuration + user assets
- Build Execution DAG based on requirements
- Dispatch jobs to agents in parallel
- Track state transitions via state machine
- Enforce retry limits, timeouts, and loop boundaries
- Emit structured logs for every state change

**Key Files:**
- `orchestration_agent.py` - Main orchestrator
- `dag.py` - DAG builder and executor
- `state_machine.py` - Deterministic state management

---

### 2. Deep Research Agent (On-Demand)
**Location:** `server/app/agents/research/deep_research_agent.py`

Triggered only when:
- Topic = trending / news
- User enables "factual mode"
- Long-form or educational content

**Outputs a Context Pack:**
```python
{
  "facts": [],
  "trends": [],
  "risks": [],
  "sources": [],
  "region_specifics": []
}
```

Stored in:
- Postgres (structured) via `ResearchContext` model
- Passed downstream to content agents

---

### 3. Content Agents (Pure Workers)
**Location:** `server/app/agents/content/content_agents.py`

**Agents:**
- `ScriptAgent` - Generates video scripts
- `ImageAgent` - Creates images/thumbnails
- `AudioAgent` - Generates voiceovers
- `VideoAgent` - Creates video content

**Design Rules:**
- ✅ Stateless
- ✅ Idempotent
- ✅ Retryable
- ✅ No shared memory
- ✅ No orchestration logic
- ✅ No cross-agent communication

**Parallelism:**
- Script + Image + Audio run in parallel
- Video depends on Script and/or Image outputs

---

### 4. Quality Check Agent (Gatekeeper)
**Location:** `server/app/agents/quality/quality_check_agent.py`

**Critical for product-grade output.**

**Validates:**
- ✅ Length/duration compliance
- ✅ Tone match
- ✅ Factual consistency vs Context Pack
- ✅ Platform compliance rules
- ✅ Brand safety
- ✅ Technical quality

**Outputs:**
```python
{
  "status": "PASS" | "SOFT_FAIL" | "HARD_FAIL",
  "reasons": [],
  "score": 0.0-1.0
}
```

**Feedback to Orchestrator:**
- `PASS` → Continue
- `SOFT_FAIL` → Regenerate specific step
- `HARD_FAIL` → Halt pipeline + notify user

---

### 5. Composer Agent (Final Assembly)
**Location:** `server/app/agents/composer/composer_agent.py`

**Combines everything:**
- Script + Audio (voiceover)
- Video clips / images / scenes
- Synchronizes into final video with audio, transitions, captions

**Outputs:**
- Final assembled video
- Metadata for posting
- Subtitle/caption files

---

### 6. Loop Control & Failure Policy
**Location:** `server/app/orchestration/state_machine.py`

**Hard Guarantees:**
```python
max_retries_per_step = 2
max_total_failures = 5
max_runtime = 30 minutes
```

**Pipeline State Machine:**
```
INIT → RUNNING → PARTIAL_FAIL → RETRY → HARD_FAIL → HALTED
                            ↓
                        COMPLETED
```

**Rules:**
- ❌ No infinite loops
- ❌ No unbounded retries
- ✅ Any step exceeding retry budget → pipeline FAILED
- ✅ Emit event: `PIPELINE_RUN_FAILED`
- ✅ User notified via dashboard

---

### 7. Logging & Observability
**Location:** `server/app/logging_system/pipeline_logger.py`

**Every agent interaction emits:**
```python
{
  "pipeline_run_id": "...",
  "step_name": "script",
  "agent_name": "ScriptAgent",
  "state": "START" | "SUCCESS" | "FAIL" | "RETRY",
  "timestamp": "2024-01-26T10:03:00Z",
  "payload_summary": {...},
  "error": "..." (optional)
}
```

**Stored in:**
- Append-only log store (`PipelineEvent` model)
- Indexed by `pipeline_run_id`

**Dashboard streams logs like:**
```
[10:01] ResearchAgent START
[10:03] ResearchAgent SUCCESS
[10:03] ScriptAgent START
[10:05] ScriptAgent FAIL (hallucination)
[10:05] Orchestrator RETRY ScriptAgent (1/2)
[10:06] ScriptAgent SUCCESS
...
```

---

### 8. Celery + Job Queue
**Location:** `server/app/celery_config/`

**Components:**
- `celery_app.py` - Celery configuration
- `pipeline_tasks.py` - Main pipeline execution tasks
- `tasks.py` - Individual agent tasks
- `scheduled_tasks.py` - Periodic maintenance (Celery Beat)

**Queue Structure:**
```
pipelines → High-priority pipeline orchestration
research  → Research agent tasks
content   → Content generation agents
quality   → Quality check tasks
default   → Background/utility tasks
```

**Scheduled Tasks (Celery Beat):**
- Cleanup expired results (every 6 hours)
- Monitor pipeline health (every 5 minutes)
- Clear research cache (daily)
- Generate analytics (daily)

---

## Execution Flow (Canonical)

```
Pipeline Created
  ↓
Scheduler triggers run
  ↓
Orchestration Agent
  ├─ Decide: Research needed?
  │    ├─ Yes → ResearchAgent → ContextPack
  │    └─ No  → Use cached context
  ├─ Build Execution DAG
  ├─ Run in parallel:
  │    ├─ ScriptAgent
  │    ├─ ImageAgent
  │    └─ AudioAgent
  ├─ Wait for dependencies
  ├─ VideoAgent (if required)
  ├─ QualityCheckAgent
  │    ├─ PASS → continue
  │    ├─ SOFT_FAIL → regenerate node
  │    └─ HARD_FAIL → halt
  ├─ ComposerAgent
  ├─ PostingAgent (optional)
  ├─ Mark SUCCESS
  └─ FeedbackAgent (async)
```

---

## Database Models

### PipelineRun
**Location:** `server/app/models/execution.py`

Tracks complete pipeline execution:
- State, timing, failures
- Configuration snapshot
- Final outputs and artifacts
- Error tracking
- Celery task ID

### PipelineRunStep
Individual step execution within a run:
- Step state, timing
- Retry count
- Input/output summaries
- Error details

### PipelineEvent
Append-only event log:
- Complete audit trail
- Every state transition
- Agent invocations
- Quality checks
- Failures and retries

### ResearchContext
Cached research results:
- Topic, depth, region
- Complete ContextPack
- Confidence score
- TTL management

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis (for Celery)

```bash
# Start Redis in WSL
sudo service redis-server start

# Or if using systemd in WSL2
sudo systemctl start redis

# Verify it's running
redis-cli ping  # Should return PONG
```

**Note:** Windows applications (FastAPI, Celery) will connect to `localhost:6379` which automatically bridges to WSL Redis.

### 3. Run Database Migrations

```bash
cd server
alembic upgrade head
```

### 4. Start Celery Worker

```bash
cd server
celery -A app.celery_config.celery_app worker --loglevel=info --pool=solo
```

### 5. Start Celery Beat (Scheduler)

```bash
cd server
celery -A app.celery_config.celery_app beat --loglevel=info
```

### 6. Start FastAPI Server

```bash
cd server
uvicorn main:app --reload
```

---

## Testing Pipeline Execution

### Via Celery Task

```python
from app.celery_config.pipeline_tasks import execute_pipeline

result = execute_pipeline.delay(
    pipeline_id="pipeline_123",
    pipeline_run_id="run_20240126_001",
    pipeline_config={
        "content_type": "short_video",
        "platform": "youtube",
        "topic": "AI News",
        "tone": "professional",
        "duration_seconds": 60,
        "generate_images": True,
        "generate_audio": True
    },
    user_assets={}
)

# Check status
print(result.status)
print(result.result)
```

### Via Orchestrator Directly

```python
import asyncio
from app.orchestration.orchestration_agent import OrchestrationAgent

async def test_pipeline():
    orchestrator = OrchestrationAgent()
    
    result = await orchestrator.execute_pipeline(
        pipeline_id="test_pipeline",
        pipeline_run_id="test_run_001",
        pipeline_config={
            "content_type": "educational",
            "platform": "youtube",
            "topic": "Python Programming",
            "tone": "educational",
            "duration_seconds": 120
        },
        user_assets={}
    )
    
    print(f"Final State: {result.state.value}")
    print(f"Duration: {result.duration_seconds}s")

asyncio.run(test_pipeline())
```

---

## Configuration

### Execution Policy

Customize in `ExecutionPolicy`:

```python
policy = ExecutionPolicy(
    max_retries_per_step=2,      # Retries per individual step
    max_total_failures=5,         # Total failures before halt
    max_runtime_minutes=30,       # Maximum pipeline runtime
    step_timeout_seconds=300,     # Timeout per step
    enable_parallel_execution=True  # Enable parallel agent execution
)
```

### Celery Configuration

Edit `server/app/celery_config/celery_app.py`:

```python
# Redis connection
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Worker settings
worker_concurrency = 4
worker_max_tasks_per_child = 50

# Task limits
task_time_limit = 1800  # 30 minutes
task_soft_time_limit = 1500  # 25 minutes
```

---

## API Integration (TODO)

Integrate with your existing FastAPI endpoints:

### Create Pipeline Run

```python
@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline_endpoint(
    pipeline_id: str,
    config: PipelineConfig,
    current_user: User = Depends(get_current_user)
):
    # Generate run ID
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Queue pipeline execution
    task = execute_pipeline.delay(
        pipeline_id=pipeline_id,
        pipeline_run_id=run_id,
        pipeline_config=config.dict(),
        user_assets={}
    )
    
    return {
        "run_id": run_id,
        "task_id": task.id,
        "status": "queued"
    }
```

### Get Pipeline Status

```python
@router.get("/runs/{run_id}/status")
async def get_run_status(
    run_id: str,
    db: Session = Depends(get_db)
):
    run = db.query(PipelineRun).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404)
    
    return run.to_dict()
```

### Stream Logs

```python
@router.get("/runs/{run_id}/logs")
async def stream_logs(
    run_id: str,
    db: Session = Depends(get_db)
):
    events = db.query(PipelineEvent).filter_by(
        run_id=run_id
    ).order_by(PipelineEvent.timestamp).all()
    
    return [event.to_dict() for event in events]
```

---

## Architecture Principles

This system is:

✅ **A mini Temporal / Airflow / Prefect**
✅ **Purpose-built for LLM + media agents**
✅ **Deterministic**
✅ **Observable**
✅ **Restartable**
✅ **Bounded**
✅ **Auditable**

Every pipeline run is a **finite execution graph**, not a chain of prompts.

---

## Next Steps

1. **Integrate LLM Providers**
   - Add OpenAI, Anthropic, etc. to content agents
   - Implement actual script/content generation

2. **Integrate Media APIs**
   - DALL-E, Midjourney for images
   - ElevenLabs, Google TTS for audio
   - Runway, D-ID for video

3. **Add Posting Agents**
   - YouTube API integration
   - TikTok, Instagram posting
   - Platform-specific optimizations

4. **Dashboard Integration**
   - Real-time log streaming
   - Pipeline monitoring UI
   - Execution graphs visualization

5. **Vector Database**
   - Store research contexts in vector DB
   - Semantic search for reuse

6. **LangGraph Integration**
   - Use LangGraph for complex agent workflows
   - Multi-agent coordination
   - Tool use and function calling

---

## File Structure

```
server/app/
├── agents/                      # Agent implementations
│   ├── base_agent.py           # Base agent interface
│   ├── research/               # Research agents
│   │   └── deep_research_agent.py
│   ├── content/                # Content generation agents
│   │   └── content_agents.py   # Script, Image, Audio, Video
│   ├── quality/                # Quality control
│   │   └── quality_check_agent.py
│   └── composer/               # Final assembly
│       └── composer_agent.py
│
├── orchestration/              # Orchestration engine
│   ├── orchestration_agent.py  # Main orchestrator
│   ├── dag.py                  # DAG builder and executor
│   └── state_machine.py        # State management
│
├── logging_system/             # Observability
│   └── pipeline_logger.py      # Structured logging
│
├── celery_config/              # Job queue
│   ├── celery_app.py          # Celery configuration
│   ├── pipeline_tasks.py       # Main pipeline tasks
│   ├── tasks.py                # Agent tasks
│   └── scheduled_tasks.py      # Periodic tasks
│
└── models/                     # Database models
    └── execution.py            # Execution tracking models
```

---

## License

MIT

---

## Support

For issues or questions, please open a GitHub issue.
