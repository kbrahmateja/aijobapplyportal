import os
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
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
    expose_headers=["Content-Disposition"],
)

from routers import job, resume, matching, application
import auth

# app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) # Auth handled by Clerk/Dependency
app.include_router(job.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(resume.router, prefix="/api/resumes", tags=["resumes"], dependencies=[Depends(auth.get_current_user)])
app.include_router(matching.router, prefix="/api/resumes", tags=["matching"], dependencies=[Depends(auth.get_current_user)])
app.include_router(application.router, prefix="/api/applications", tags=["applications"], dependencies=[Depends(auth.get_current_user)])

TEMP_DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "temp_downloads")

@app.get("/api/resumes/download/{file_id}")
async def download_tailored_pdf(file_id: str, filename: str = "Tailored_Resume.pdf"):
    """
    Downloads a temporarily stored tailored PDF file without requiring Bearer auth.
    This allows native browser <a href="..." download> to work correctly.
    """
    filepath = os.path.join(TEMP_DOWNLOADS_DIR, f"{file_id}.pdf")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File expired or not found")
        
    return FileResponse(
        filepath, 
        media_type="application/pdf", 
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

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
