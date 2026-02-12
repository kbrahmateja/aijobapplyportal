from database import SessionLocal
from models import Job
from sqlalchemy import func

def analyze_jobs():
    db = SessionLocal()
    
    # Count by source
    results = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()
    
    print("\n--- Jobs by Source ---")
    if not results:
        print("No jobs found.")
    for source, count in results:
        print(f"Source: {source} | Count: {count}")
        
    print("\n--- Recent Jobs (Top 10) ---")
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(10).all()
    for j in jobs:
        print(f"- [{j.source}] {j.title} at {j.company}")
    
    db.close()

if __name__ == "__main__":
    analyze_jobs()
