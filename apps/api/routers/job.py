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

# Terms that mean "available from anywhere in the world"
WORLDWIDE_TERMS = [
    "worldwide", "anywhere", "global", "international",
    "remote", "work from home", "wfh", "distributed"
]

def is_worldwide_term(location: str) -> bool:
    """Returns True if the location query itself means worldwide/remote."""
    loc_lower = location.lower()
    return any(wt in loc_lower for wt in WORLDWIDE_TERMS)

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
    Get jobs with intelligent filtering and pagination.
    Location filter uses smart OR logic — specific location queries also include
    worldwide/remote/anywhere jobs since those are available from any country.
    """
    query = db.query(Job)
    
    # ── Search filter ──────────────────────────────────────────────────────────
    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.company.ilike(f"%{search}%"),
            Job.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # ── Location filter (INTELLIGENT) ─────────────────────────────────────────
    # Strategy:
    #   a) Match jobs whose location field contains any of the search tokens
    #   b) If the query is for a specific geography (not "remote"/"worldwide" itself),
    #      ALSO include worldwide/remote/anywhere/null jobs (universally available)
    if location:
        loc_stripped = location.strip()
        tokens = [t.strip() for t in loc_stripped.replace(',', ' ').split() if len(t.strip()) > 1]
        
        conditions = []
        
        # (a) Direct token matches — OR across tokens for flexibility
        for token in tokens:
            conditions.append(Job.location.ilike(f"%{token}%"))
        
        # (b) Worldwide fallback — only when user isn't already searching for "remote"/"worldwide"
        if not is_worldwide_term(loc_stripped):
            for wt in WORLDWIDE_TERMS:
                conditions.append(Job.location.ilike(f"%{wt}%"))
            # Also include NULL/empty location (many scrapers omit location for remote roles)
            conditions.append(Job.location.is_(None))
            conditions.append(Job.location == "")
        
        query = query.filter(or_(*conditions))
    
    # ── Source filter ─────────────────────────────────────────────────────────
    if source:
        query = query.filter(Job.source == source)
    
    # ── Pagination ────────────────────────────────────────────────────────────
    total = query.count()
    total_pages = (total + limit - 1) // limit
    skip = (page - 1) * limit
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
    # All unique non-empty locations
    locations = db.query(Job.location).filter(
        Job.location.isnot(None),
        Job.location != ""
    ).distinct().all()
    locations = sorted([loc[0] for loc in locations if loc[0] and len(loc[0]) < 80])
    
    # All sources
    sources = db.query(Job.source).distinct().all()
    sources = [src[0] for src in sources if src[0]]
    
    categories = ["All", "Engineering", "Design", "Product", "Marketing", "Data"]
    total_jobs = db.query(Job).count()
    
    return FiltersResponse(
        categories=categories,
        locations=locations,
        sources=sources,
        total_jobs=total_jobs
    )
