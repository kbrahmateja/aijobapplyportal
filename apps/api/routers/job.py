from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from database import get_db
from models import Job
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class JobSchema(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str
    source: str
    posted_at: datetime | None = None
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: List[JobSchema]
    total: int
    page: int
    limit: int
    total_pages: int

class FiltersResponse(BaseModel):
    categories: List[str]
    locations: List[str]
    sources: List[str]
    total_jobs: int

@router.get("/", response_model=JobListResponse)
def get_jobs(
    search: Optional[str] = Query(None, description="Search in title, company, description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    source: Optional[str] = Query(None, description="Filter by source"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Jobs per page"),
    db: Session = Depends(get_db)
):
    """
    Get jobs with advanced filtering and pagination.
    """
    query = db.query(Job)
    
    # Apply search filter
    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.company.ilike(f"%{search}%"),
            Job.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply location filter — match each word/token independently (AND logic)
    # so "Remote India" matches jobs that have both "Remote" and "India" in location
    if location:
        terms = [t.strip() for t in location.replace(',', ' ').split() if t.strip()]
        for term in terms:
            query = query.filter(Job.location.ilike(f"%{term}%"))
    
    # Apply source filter
    if source:
        query = query.filter(Job.source == source)
    
    # Get total count before pagination
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit  # Ceiling division
    skip = (page - 1) * limit
    
    # Apply pagination and ordering
    jobs = query.order_by(Job.posted_at.desc()).offset(skip).limit(limit).all()
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get("/filters", response_model=FiltersResponse)
def get_filters(db: Session = Depends(get_db)):
    """
    Get available filter options and metadata.
    """
    # Get unique locations (excluding None/empty)
    locations = db.query(Job.location).filter(Job.location.isnot(None)).distinct().all()
    locations = [loc[0] for loc in locations if loc[0]]
    
    # Get unique sources
    sources = db.query(Job.source).distinct().all()
    sources = [src[0] for src in sources]
    
    # Extract categories from job titles (basic heuristic)
    # In production, you'd have a dedicated category column
    categories = ["All", "Engineering", "Design", "Product", "Marketing", "Data"]
    
    # Get total job count
    total_jobs = db.query(Job).count()
    
    return FiltersResponse(
        categories=categories,
        locations=sorted(locations),  # All unique locations
        sources=sources,
        total_jobs=total_jobs
    )
