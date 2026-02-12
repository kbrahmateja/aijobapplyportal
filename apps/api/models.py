from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from pgvector.sqlalchemy import Vector
import enum

class SubscriptionTier(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    EXPERT = "EXPERT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=True) # Nullable for legacy support
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True) # Nullable as we move to Clerk
    is_active = Column(Boolean, default=True)
    
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    daily_quota = Column(Integer, default=1)
    quota_used_today = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Application", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    description = Column(Text)
    url = Column(String, unique=True)
    source = Column(String)  # e.g., "linkedin", "indeed"
    posted_at = Column(DateTime(timezone=True))
    embedding = Column(Vector(1536))  # Semantic embedding of the job description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    applications = relationship("Application", back_populates="job")

from pgvector.sqlalchemy import Vector

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)  # Parsed text content
    structured_data = Column(JSON, nullable=True) # JSON extraction of skills, exp, etc.
    embedding = Column(Vector(1536))  # 1536 dimensions for OpenAI text-embedding-3-small
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    status = Column(String, default="pending")  # pending, queued, applied, rejected, interview
    cover_letter = Column(Text)
    match_score = Column(Float, nullable=True)
    decision_reason = Column(Text, nullable=True) # Why it was queued/rejected
    scheduled_at = Column(DateTime(timezone=True), nullable=True) # When to execute
    applied_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
