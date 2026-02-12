from typing import List
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from database import get_db
from models import Job
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="AI Job Application Platform API")

class JobSchema(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str
    source: str
    posted_at: datetime
    
    class Config:
        from_attributes = True

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import job, resume, matching, application
import auth

# app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) # Auth handled by Clerk/Dependency
app.include_router(job.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(resume.router, prefix="/api/resumes", tags=["resumes"], dependencies=[Depends(auth.get_current_user)])
app.include_router(matching.router, prefix="/api/resumes", tags=["matching"], dependencies=[Depends(auth.get_current_user)])
app.include_router(application.router, prefix="/api/applications", tags=["applications"], dependencies=[Depends(auth.get_current_user)])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Job Application Copilot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/jobs", response_model=List[JobSchema])
async def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs
