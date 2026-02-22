"""
Celery Beat scheduler startup script.
Starts Celery Beat for periodic tasks.
"""

import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_config.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery Beat
    celery_app.Beat().run()
