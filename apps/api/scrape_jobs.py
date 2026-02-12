from database import SessionLocal
from services.browser.job_scraper import JobScraper
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_scraper():
    db = SessionLocal()
    scraper = JobScraper(db)
    
    print("--- Starting Job Scraper ---")
    try:
        # Scrape Python Jobs
        count = scraper.scrape_weworkremotely(search_term="python")
        print(f"Successfully scraped {count} jobs.")
        
        # Scrape AI Jobs
        count_ai = scraper.scrape_weworkremotely(search_term="AI")
        print(f"Successfully scraped {count_ai} AI jobs.")

        # Scrape React Jobs
        count_react = scraper.scrape_weworkremotely(search_term="React")
        print(f"Successfully scraped {count_react} React jobs.")

        # Scrape Frontend Jobs
        count_frontend = scraper.scrape_weworkremotely(search_term="Frontend")
        print(f"Successfully scraped {count_frontend} Frontend jobs.")
        
    except Exception as e:
        print(f"Scraper failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()
