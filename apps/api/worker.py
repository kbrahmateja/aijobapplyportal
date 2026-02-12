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

def run_worker():
    logger.info("Starting Application Execution Worker...")
    db = SessionLocal()
    agent = ApplicationExecutionAgent(db)
    
    try:
        while True:
            agent.process_queue()
            # Sleep for a bit to avoid hammering DB
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
    finally:
        db.close()

if __name__ == "__main__":
    run_worker()
