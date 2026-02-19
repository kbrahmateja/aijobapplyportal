from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Celery app definition
# ──────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "aijobapplyportal",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.scraping_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks once after 60s
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Beat schedule — daily at 2 AM UTC
    beat_schedule={
        "daily-job-scraping": {
            "task": "tasks.scraping_tasks.scrape_all_jobs_task",
            "schedule": crontab(hour=2, minute=0),
            "options": {"expires": 3600},
        },
    },
)

# Make `celery_app` importable as `app` for Celery CLI convention
app = celery_app
