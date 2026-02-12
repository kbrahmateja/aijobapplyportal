from typing import List, Dict, Any
import asyncio
from datetime import datetime
from .scraper import JobScraper

class MockJobScraper(JobScraper):
    """
    A mock scraper for testing purposes.
    Returns fake job data without making external network requests.
    """
    
    def __init__(self):
        super().__init__(platform_name="mock_source")

    async def scrape(self, query: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Simulate network delay
        await asyncio.sleep(1)
        
        jobs = []
        for i in range(limit):
            jobs.append({
                "title": f"{query} Engineer {i+1}",
                "company": f"Tech Corp {i+1}",
                "location": location,
                "description": f"We are looking for a skilled {query} engineer to join our team...",
                "url": f"https://example.com/jobs/{i+1}",
                "posted_at": datetime.now(),
                "source": self.platform_name
            })
            
        return jobs
