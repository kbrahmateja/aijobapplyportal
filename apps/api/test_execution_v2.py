import os
import uuid
from datetime import datetime, timezone
from database import SessionLocal
from models import Application, User, Job, Resume
from agents.execution_agent import ApplicationExecutionAgent

def test_execution_v2():
    print("--- Testing Execution Agent v2 (Real Browser) ---")
    
    db = SessionLocal()
    agent = ApplicationExecutionAgent(db)
    
    # 1. Setup Test Data
    user = User(
        clerk_id=f"test_user_{uuid.uuid4()}",
        email=f"test_{uuid.uuid4()}@example.com"
    )
    db.add(user)
    db.commit()
    
    # Create Job (LinkedIn URL)
    # Using a generic LinkedIn Jobs search URL or a specific easy apply one would be better
    # But for safety we might just use a known safe URL or expect it to fail gracefully
    job_url = f"https://www.linkedin.com/jobs/view/{uuid.uuid4()}" 
    job = Job(
        title="Test Engineer",
        company="Tech Corp",
        url=job_url,
        source="LinkedIn",
        posted_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    
    # Create Resume
    resume = Resume(
        user_id=user.id,
        structured_data={"skills": ["Python"]},
        content="Dummy Resume Text"
    )
    db.add(resume)
    db.commit()
    
    # Create queued Application
    app = Application(
        user_id=user.id,
        job_id=job.id,
        resume_id=resume.id,
        status="queued",
        scheduled_at=datetime.now(timezone.utc)
    )
    db.add(app)
    db.commit()
    
    print(f"Created queued application {app.id} for job {job_url}")
    
    # 2. Run the Agent
    # This should trigger the browser launch
    print("Running process_queue()... (Watch for browser window)")
    agent.process_queue()
    
    # 3. Verify Result
    db.refresh(app)
    print(f"Final Application Status: {app.status}")
    print(f"Decision Reason: {app.decision_reason}")
    
    # Cleanup
    db.delete(app)
    db.delete(resume)
    db.delete(job)
    db.delete(user)
    db.commit()
    db.close()

if __name__ == "__main__":
    test_execution_v2()
