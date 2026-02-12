import sys
sys.path.insert(0, '/Users/brahmatejakanchibhotla/Documents/projects/aijobapplyportal/apps/api')

from database import SessionLocal
from models import Job
import json

try:
    db = SessionLocal()
    jobs = db.query(Job).limit(3).all()
    
    # Try to serialize
    for job in jobs:
        print(f"\nJob ID: {job.id}")
        print(f"  Title: {job.title}")
        print(f"  Company: {job.company}")
        print(f"  Location: {job.location}")
        print(f"  Description: {job.description[:50] if job.description else None}...")
        print(f"  URL: {job.url}")
        print(f"  Source: {job.source}")
        print(f"  Posted At: {job.posted_at}")
        print(f"  Embedding: {type(job.embedding)}")
        
        # Try to convert to dict (Pydantic way)
        from routers.job import JobSchema
        try:
            schema = JobSchema.model_validate(job)
            print(f"  ✅ Serialization successful")
        except Exception as e:
            print(f"  ❌ Serialization failed: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
