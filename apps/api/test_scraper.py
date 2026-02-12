import asyncio
import sys
import os

# Add the current directory to sys.path so we can import from apps.api
sys.path.append(os.getcwd())

from agents.job_discovery.mock_scraper import MockJobScraper
from services.resume.embedding import EmbeddingService
from database import SessionLocal
from models import Job
from sqlalchemy.orm import Session

async def run_scraper():
    print("Initializing Mock Scraper...")
    scraper = MockJobScraper()
    embedding_service = EmbeddingService()
    
    print("Scraping jobs...")
    jobs_data = await scraper.scrape(query="AI Engineer", location="Remote", limit=5)
    
    print(f"Found {len(jobs_data)} jobs.")
    
    db: Session = SessionLocal()
    try:
        for job_data in jobs_data:
            # Check if job exists
            existing_job = db.query(Job).filter(Job.url == job_data["url"]).first()
            if not existing_job:
                # Generate embedding
                text_content = f"{job_data['title']} {job_data['description']}"
                job_data["embedding"] = embedding_service.generate_embedding(text_content)
                
                new_job = Job(**job_data)
                db.add(new_job)
                print(f"Added job: {new_job.title}")
            else:
                print(f"Job already exists: {job_data['title']}")
        
        db.commit()
        print("Database commited successfully.")
        
    except Exception as e:
        print(f"Error saving to DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
