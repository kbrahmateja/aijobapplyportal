from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, Job
from typing import List, Any
from pydantic import BaseModel

router = APIRouter()

class JobMatchSchema(BaseModel):
    id: int
    title: str
    company: str
    similarity: float
    url: str
    location: str
    description: str
    source: str
    posted_at: str | None = None

from auth import get_current_user
from models import Resume, Job, User

@router.get("/{resume_id}/matches", response_model=List[JobMatchSchema])
async def get_job_matches(
    resume_id: int, 
    limit: int = 10, 
    min_similarity: float = 0.0, # Default to 0 to show all
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Get Resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")
    
    if resume.embedding is None:
        raise HTTPException(status_code=400, detail="Resume has no embedding")

    # 2. Perform Vector Search (Cosine Similarity)
    # Note: pgvector's cosine_distance operator is <=>
    # We want similarity, which is 1 - distance
    
    similarity_expr = (1 - Job.embedding.cosine_distance(resume.embedding)).label("similarity")
    
    query = db.query(Job, similarity_expr)
    
    # Filter by threshold if provided
    if min_similarity > 0:
        query = query.filter((1 - Job.embedding.cosine_distance(resume.embedding)) >= min_similarity)
        
    jobs = query.order_by(
        Job.embedding.cosine_distance(resume.embedding)
    ).limit(limit).all()
    
    # 3. Format Response
    results = []
    for job, similarity in jobs:
        results.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "similarity": float(similarity),
            "url": job.url,
            "location": job.location,
            "description": job.description,
            "source": job.source,
            "posted_at": job.posted_at.isoformat() if job.posted_at else None
        })
        
    return results
