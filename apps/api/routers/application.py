from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Job, Resume, Application
from auth import get_current_user
from agents.decision_agent import ApplicationDecisionAgent
from pydantic import BaseModel
from datetime import datetime
import numpy as np

router = APIRouter()

class ApplicationResponse(BaseModel):
    id: int
    status: str
    decision_reason: str | None
    scheduled_at: datetime | None

class ApplyRequest(BaseModel):
    resume_id: int
    match_score: float = 0.0

@router.post("/{job_id}/apply", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: int, 
    request: ApplyRequest,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Validate Job/Resume
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this resume")

    # 2. Calculate Match Score
    match_score = request.match_score
    
    if resume.embedding is not None and job.embedding is not None:
         try:
             # Convert to numpy arrays if they aren't already (pgvector returns list)
             v1 = np.array(resume.embedding)
             v2 = np.array(job.embedding)
             match_score = float(np.dot(v1, v2))
         except Exception:
             # Fallback to provided score if calc fails
             pass

    # 3. Invoke Decision Agent
    agent = ApplicationDecisionAgent(db)
    try:
        application = agent.decide_and_queue(
            user=current_user,
            job_id=job_id,
            resume_id=request.resume_id,
            match_score=match_score
        )
        return ApplicationResponse(
            id=application.id,
            status=application.status,
            decision_reason=application.decision_reason,
            scheduled_at=application.scheduled_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ApplicationResponse])
async def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all applications for the current user.
    """
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).order_by(Application.created_at.desc()).all()
    
    return applications
