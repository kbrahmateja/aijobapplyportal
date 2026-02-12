from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class JobScraper(ABC):
    """
    Abstract Base Class for Job Scrapers.
    Each platform (LinkedIn, Indeed, etc.) will have its own implementation.
    """
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    @abstractmethod
    async def scrape(self, query: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape jobs from the source.
        
        Args:
            query: Job title or keywords
            location: Job location
            limit: Max number of jobs to fetch
            
        Returns:
            List of job dictionaries with standardized keys:
            - title
            - company
            - location
            - description (if available)
            - url
            - posted_at (datetime)
            - source (self.platform_name)
        """
        pass

    def normalize_job_data(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to normalize raw data into the schema expected by the database.
        """
        return {
            "title": raw_job.get("title"),
            "company": raw_job.get("company"),
            "location": raw_job.get("location"),
            "description": raw_job.get("description", ""),
            "url": raw_job.get("url"),
            "source": self.platform_name,
            "posted_at": raw_job.get("posted_at", datetime.now()),
        }
