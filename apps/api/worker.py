"""
Worker entry point.

Start the Celery worker + Beat scheduler on Render with:
  celery -A celery_app worker --loglevel=info --beat

For a separate Celery Beat scheduler process (recommended for prod):
  celery -A celery_app beat --loglevel=info

For local development with application queue only:
  celery -A celery_app worker --loglevel=info
"""
import time
import logging
from database import SessionLocal
from agents.execution_agent import ApplicationExecutionAgent

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("worker")


def run_application_worker():
    """
    Long-polling worker that processes queued job applications.
    Runs separately from the Celery scraping worker.
    """
    logger.info("Starting Application Execution Worker...")
    db = SessionLocal()
    agent = ApplicationExecutionAgent(db)

    try:
        while True:
            agent.process_queue()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
    finally:
        db.close()


if __name__ == "__main__":
    run_application_worker()
