import logging
from datetime import datetime
from services.browser.browser_manager import BrowserManager
from sqlalchemy.orm import Session
from models import Job
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def scrape_weworkremotely(self, search_term: str = "python"):
        """
        Scrapes WeWorkRemotely for jobs matching the search_term.
        """
        url = f"https://weworkremotely.com/remote-jobs/search?term={search_term}"
        self.logger.info(f"Scraping URL: {url}")
        
        new_jobs_count = 0
        
        with BrowserManager(headless=True) as page:
            page.goto(url)
            # Wait for content to load
            page.wait_for_selector(".jobs-container", timeout=10000)
            
            # Get HTML content
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # WWR structure: section.jobs article ul li
            job_items = soup.select("section.jobs article ul li")
            
            self.logger.info(f"Found {len(job_items)} potential job items.")
            
            for item in job_items:
                # Filter out "view all" or ad items if any
                if "view-all" in item.get("class", []):
                    continue
                    
                try:
                    # Correct Selectors for WeWorkRemotely
                    title_elem = item.select_one(".new-listing__header__title")
                    company_elem = item.select_one(".new-listing__company-name")
                    region_elem = item.select_one(".new-listing__company-headquarters")
                    
                    if not title_elem or not company_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    # Company text often has nested elements, standard get_text is fine
                    company = company_elem.get_text(strip=True)
                    location = region_elem.get_text(strip=True) if region_elem else "Remote"
                    
                    # Link logic: Find the unlocked link or first link
                    link_elem = item.select_one("a.listing-link--unlocked") or item.select_one("a")
                    
                    if not link_elem:
                        continue
                        
                    href = link_elem['href']
                    if not href.startswith("http"):
                        href = f"https://weworkremotely.com{href}"
                        
                    # Check duplication
                    exists = self.db.query(Job).filter(Job.url == href).first()
                    if exists:
                        continue
                        
                    # Create Job
                    job = Job(
                        title=title,
                        company=company,
                        location=location,
                        description=f"Scraped from WeWorkRemotely. Search term: {search_term}", 
                        url=href,
                        source="WeWorkRemotely",
                        posted_at=datetime.utcnow() 
                    )
                    self.db.add(job)
                    new_jobs_count += 1
                    print(f"Added Job: {title} at {company}")
                    
                except Exception as e:
                    self.logger.error(f"Error parsing item: {e}")
                    continue
            
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                self.logger.error(f"Commit failed: {e}")

        self.logger.info(f"Scraping complete. Added {new_jobs_count} new jobs.")
        return new_jobs_count
