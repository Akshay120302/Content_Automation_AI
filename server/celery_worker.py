"""
Celery worker startup script.
Starts Celery worker for processing pipeline tasks.
"""

import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_config.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Use solo pool for Windows compatibility
        '--concurrency=4',
        '--max-tasks-per-child=50'
    ])
