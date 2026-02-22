"""
Celery configuration for distributed task execution.
Manages job queue, scheduling, and background processing.
"""

from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange
import os


# Celery app configuration
def create_celery_app(
    broker_url: str = None,
    result_backend: str = None,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0
) -> Celery:
    """
    Create and configure Celery application.
    
    Args:
        broker_url: Message broker URL (Redis/RabbitMQ)
        result_backend: Result backend URL
        redis_host: Redis host
        redis_port: Redis port
        redis_db: Redis database number
        
    Returns:
        Configured Celery app
    """
    # Default to Redis if not specified
    if not broker_url:
        broker_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
    
    if not result_backend:
        result_backend = f"redis://{redis_host}:{redis_port}/{redis_db + 1}"
    
    app = Celery(
        'content_automation',
        broker=broker_url,
        backend=result_backend,
        include=[
            'app.celery_config.tasks',
            'app.celery_config.pipeline_tasks',
            'app.celery_config.scheduled_tasks'
        ]
    )
    
    # Celery configuration
    app.conf.update(
        # Task settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task execution settings
        task_track_started=True,
        task_time_limit=1800,  # 30 minutes hard limit
        task_soft_time_limit=1500,  # 25 minutes soft limit
        task_acks_late=True,  # Acknowledge after completion
        task_reject_on_worker_lost=True,
        
        # Result backend settings
        result_expires=3600,  # Results expire after 1 hour
        result_extended=True,
        
        # Worker settings
        worker_prefetch_multiplier=1,  # One task at a time per worker
        worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
        worker_disable_rate_limits=False,
        
        # Concurrency
        worker_concurrency=4,  # Number of concurrent workers
        
        # Task routing
        task_routes={
            'app.celery_config.pipeline_tasks.execute_pipeline': {
                'queue': 'pipelines',
                'routing_key': 'pipeline.execute'
            },
            'app.celery_config.tasks.research_task': {
                'queue': 'research',
                'routing_key': 'agent.research'
            },
            'app.celery_config.tasks.content_generation_task': {
                'queue': 'content',
                'routing_key': 'agent.content'
            },
            'app.celery_config.tasks.quality_check_task': {
                'queue': 'quality',
                'routing_key': 'agent.quality'
            }
        },
        
        # Task queues
        task_queues=(
            Queue('pipelines', Exchange('pipelines'), routing_key='pipeline.#'),
            Queue('research', Exchange('agents'), routing_key='agent.research'),
            Queue('content', Exchange('agents'), routing_key='agent.content'),
            Queue('quality', Exchange('agents'), routing_key='agent.quality'),
            Queue('default', Exchange('default'), routing_key='default')
        ),
        
        # Default queue
        task_default_queue='default',
        task_default_exchange='default',
        task_default_routing_key='default',
        
        # Beat schedule (for periodic tasks)
        beat_schedule={
            'cleanup-expired-results': {
                'task': 'app.celery_config.scheduled_tasks.cleanup_expired_results',
                'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
            },
            'monitor-pipeline-health': {
                'task': 'app.celery_config.scheduled_tasks.monitor_pipeline_health',
                'schedule': crontab(minute='*/5'),  # Every 5 minutes
            },
            'clear-research-cache': {
                'task': 'app.celery_config.scheduled_tasks.clear_research_cache',
                'schedule': crontab(minute=0, hour=0),  # Daily at midnight
            }
        }
    )
    
    return app


# Create default Celery app instance
celery_app = create_celery_app(
    redis_host=os.getenv('REDIS_HOST', 'localhost'),
    redis_port=int(os.getenv('REDIS_PORT', 6379)),
    redis_db=int(os.getenv('REDIS_DB', 0))
)


# Task priorities
class TaskPriority:
    """Task priority levels."""
    CRITICAL = 9
    HIGH = 7
    NORMAL = 5
    LOW = 3
    BACKGROUND = 1


# Retry policies
class RetryPolicy:
    """Standard retry policies for tasks."""
    
    # Exponential backoff
    EXPONENTIAL = {
        'max_retries': 3,
        'autoretry_for': (Exception,),
        'retry_backoff': True,
        'retry_backoff_max': 600,  # 10 minutes
        'retry_jitter': True
    }
    
    # Linear backoff
    LINEAR = {
        'max_retries': 5,
        'autoretry_for': (Exception,),
        'retry_backoff': 60,  # 1 minute
        'retry_jitter': False
    }
    
    # No retry
    NO_RETRY = {
        'max_retries': 0
    }
    
    # API call retry (for rate limits)
    API_RETRY = {
        'max_retries': 10,
        'autoretry_for': (Exception,),
        'retry_backoff': True,
        'retry_backoff_max': 300,
        'retry_jitter': True
    }


# Task decorators with common configurations
def pipeline_task(**kwargs):
    """Decorator for pipeline tasks."""
    default_kwargs = {
        'bind': True,
        'queue': 'pipelines',
        'time_limit': 1800,
        **RetryPolicy.EXPONENTIAL
    }
    default_kwargs.update(kwargs)
    return celery_app.task(**default_kwargs)


def agent_task(**kwargs):
    """Decorator for agent tasks."""
    default_kwargs = {
        'bind': True,
        'queue': 'content',
        'time_limit': 600,
        **RetryPolicy.LINEAR
    }
    default_kwargs.update(kwargs)
    return celery_app.task(**default_kwargs)


def research_task(**kwargs):
    """Decorator for research tasks."""
    default_kwargs = {
        'bind': True,
        'queue': 'research',
        'time_limit': 600,
        **RetryPolicy.API_RETRY
    }
    default_kwargs.update(kwargs)
    return celery_app.task(**default_kwargs)


def background_task(**kwargs):
    """Decorator for background tasks."""
    default_kwargs = {
        'bind': True,
        'queue': 'default',
        'time_limit': 300,
        **RetryPolicy.NO_RETRY
    }
    default_kwargs.update(kwargs)
    return celery_app.task(**default_kwargs)
