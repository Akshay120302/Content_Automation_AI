# Agentic Content Generation System - Quick Start

## Installation

### 1. Install Python Dependencies

```powershell
cd server
pip install -r requirements.txt
```

### 2. Start Redis in WSL

**Make sure Redis is running in your WSL environment:**

```bash
# In WSL terminal
sudo service redis-server start

# Or if using systemd
sudo systemctl start redis

# Verify Redis is running
redis-cli ping  # Should return PONG
```

**Note:** The FastAPI server and Celery workers (running on Windows) will connect to Redis via `localhost:6379`, which automatically bridges to WSL.

### 3. Run Database Migrations

```powershell
cd server
alembic upgrade head
```

This will create the new tables:
- `pipeline_runs`
- `pipeline_run_steps`
- `pipeline_events`
- `research_contexts`

## Running the System

### Terminal 1: Start FastAPI Server

```powershell
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Start Celery Worker

```powershell
cd server
python celery_worker.py
```

Or using Celery CLI:
```powershell
celery -A app.celery_config.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Start Celery Beat (Scheduler)

```powershell
cd server
python celery_beat.py
```

Or using Celery CLI:
```powershell
celery -A app.celery_config.celery_app beat --loglevel=info
```

### Terminal 4: Monitor Redis (Optional)

**In WSL terminal:**
```bash
redis-cli monitor
```

## Testing the System

### Test 1: Execute a Simple Pipeline

Create a test script `test_pipeline.py`:

```python
import asyncio
from app.orchestration.orchestration_agent import OrchestrationAgent
from app.orchestration.state_machine import ExecutionPolicy

async def test_pipeline():
    # Create orchestrator with custom policy
    policy = ExecutionPolicy(
        max_retries_per_step=2,
        max_total_failures=5,
        max_runtime_minutes=30,
        enable_parallel_execution=True
    )
    
    orchestrator = OrchestrationAgent(execution_policy=policy)
    
    # Execute pipeline
    result = await orchestrator.execute_pipeline(
        pipeline_id="test_pipeline_001",
        pipeline_run_id="run_20240126_001",
        pipeline_config={
            "content_type": "educational",
            "platform": "youtube",
            "topic": "Introduction to Python",
            "tone": "educational",
            "duration_seconds": 60,
            "generate_images": True,
            "generate_audio": True,
            "topic_type": "educational",  # Won't trigger research
            "factual_mode": False
        },
        user_assets={}
    )
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Pipeline Execution Complete!")
    print(f"{'='*60}")
    print(f"Final State: {result.state.value}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Total Failures: {result.total_failures}")
    
    if result.is_failed:
        print(f"Error: {result.error_message}")
    else:
        print(f"\nCompleted Steps:")
        for step_name, metrics in result.step_metrics.items():
            print(f"  - {step_name}: {metrics.state.value} ({metrics.retry_count} retries)")
    
    # Get execution status
    status = orchestrator.get_execution_status(result)
    print(f"\nDetailed Status:")
    print(f"  Current Step: {status['current_step']}")
    print(f"  Is Terminal: {status['is_terminal']}")
    print(f"  Is Failed: {status['is_failed']}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
```

Run it:
```powershell
cd server
python test_pipeline.py
```

### Test 2: Queue Pipeline via Celery

```python
from app.celery_config.pipeline_tasks import execute_pipeline

# Queue pipeline execution
result = execute_pipeline.delay(
    pipeline_id="pipeline_123",
    pipeline_run_id="run_20240126_002",
    pipeline_config={
        "content_type": "short_video",
        "platform": "youtube",
        "topic": "AI News Today",
        "tone": "professional",
        "duration_seconds": 60,
        "generate_images": True,
        "generate_audio": True,
        "topic_type": "news",  # Will trigger research
        "factual_mode": True
    },
    user_assets={}
)

print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")

# Wait for completion
final_result = result.get(timeout=600)  # 10 minute timeout
print(f"Final Result: {final_result}")
```

### Test 3: Individual Agent Task

```python
from app.celery_config.tasks import generate_script_task

result = generate_script_task.delay(
    pipeline_config={
        "content_type": "tutorial",
        "platform": "youtube",
        "topic": "Web Development Basics",
        "tone": "casual",
        "duration_seconds": 120
    },
    context_pack=None,
    user_assets={}
)

output = result.get()
print(f"Script Generated: {output}")
```

## Monitoring

### Check Celery Workers

```powershell
celery -A app.celery_config.celery_app inspect active
celery -A app.celery_config.celery_app inspect stats
```

### Check Celery Queues

```powershell
celery -A app.celery_config.celery_app inspect active_queues
```

### Monitor Redis Keys

```powershell
redis-cli
> KEYS *
> GET celery-task-meta-<task-id>
```

### Check Logs

Logs are stored in:
- `server/logs/pipelines/<run_id>.log`

## Architecture Verification

After running tests, verify the architecture:

1. **DAG Execution**: Check that parallel steps (Script, Image, Audio) run concurrently
2. **State Machine**: Verify state transitions in logs
3. **Retry Logic**: Introduce a failure and check retry behavior
4. **Quality Check**: Verify QC agent validates outputs
5. **Composer**: Check final video assembly

## Common Issues

### Issue: Celery can't connect to Redis

**Solution:**
```powershell
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check Redis connection in Python
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

### Issue: ImportError for modules

**Solution:**
```powershell
# Make sure you're in the server directory
cd server

# Verify PYTHONPATH
echo $env:PYTHONPATH

# Add server to path if needed
$env:PYTHONPATH = "$(pwd);$env:PYTHONPATH"
```

### Issue: Database table not found

**Solution:**
```powershell
# Run migrations
cd server
alembic upgrade head

# Verify tables exist
python -c "from app.database.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### Issue: Celery worker crashes on Windows

**Solution:**
Use `--pool=solo` or `--pool=gevent`:
```powershell
celery -A app.celery_config.celery_app worker --loglevel=info --pool=solo
```

## Environment Variables

Create `.env` file in `server/` directory:

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database
DATABASE_URL=postgresql://user:password@localhost/content_automation

# API Keys (add as needed)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# LangSmith (optional)
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=true
```

## Next Steps

1. **Integrate Real LLM Providers**: Add actual OpenAI/Anthropic API calls in agents
2. **Add Media APIs**: Integrate DALL-E, ElevenLabs, etc.
3. **Connect to Frontend**: Wire up API endpoints to your React dashboard
4. **Add Posting Agents**: Implement platform-specific posting logic
5. **Vector Database**: Add Pinecone/Weaviate for research context storage

## Production Deployment

For production:

1. **Use RabbitMQ instead of Redis** for better reliability
2. **Deploy Celery workers on separate machines**
3. **Use Flower for monitoring**: `celery -A app.celery_config.celery_app flower`
4. **Set up proper logging** (ELK stack, CloudWatch, etc.)
5. **Configure auto-scaling** for workers based on queue size
6. **Add health checks** and alerting
7. **Use environment-specific configs**

## Documentation

Full documentation available in:
- `server/app/agents/README.md` - Complete architecture guide
- Individual agent files - Detailed implementation docs
- DAG and orchestration modules - Execution flow documentation
