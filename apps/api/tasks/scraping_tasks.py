"""
Celery scraping tasks — daily job ingestion from all sources.
"""
import logging
from celery_app import celery_app
from database import SessionLocal
from services.browser.job_scraper import JobScraper

logger = logging.getLogger(__name__)

# Search terms per source (mirrors scrape_jobs.py)
WWR_TERMS = ["python", "AI", "React", "Frontend", "DevOps", "Java"]

WELLFOUND_ROLES = [
    "software-engineer",
    "machine-learning-engineer",
    "frontend-engineer",
    "backend-engineer",
    "full-stack-engineer",
    "devops-engineer",
]

MONSTER_SEARCHES = [
    ("python developer", "remote"),
    ("AI engineer", "remote"),
    ("react developer", "remote"),
    ("devops engineer", "remote"),
    ("machine learning engineer", "remote"),
]

NAUKRI_SEARCHES = [
    ("python developer", ""),
    ("artificial intelligence", ""),
    ("react js developer", ""),
    ("devops engineer", ""),
    ("machine learning engineer", ""),
    ("data engineer", ""),
]


@celery_app.task(bind=True, name="tasks.scraping_tasks.scrape_all_jobs_task", max_retries=1)
def scrape_all_jobs_task(self):
    """
    Celery task: scrape all job sources and persist to DB.
    Scheduled daily at 2 AM UTC via Celery Beat.
    Each source is independent — one failure won't stop others.
    """
    logger.info("=== [Celery] Starting daily job scraping task ===")
    db = SessionLocal()
    scraper = JobScraper(db)
    results = {}

    # ── WeWorkRemotely ─────────────────────────────────────────
    wwr_total = 0
    for term in WWR_TERMS:
        try:
            count = scraper.scrape_weworkremotely(search_term=term)
            wwr_total += count
        except Exception as e:
            logger.error(f"[WeWorkRemotely] Failed for '{term}': {e}")
    results["WeWorkRemotely"] = wwr_total

    # ── Wellfound ──────────────────────────────────────────────
    wf_total = 0
    for role in WELLFOUND_ROLES:
        try:
            count = scraper.scrape_wellfound(role=role)
            wf_total += count
        except Exception as e:
            logger.error(f"[Wellfound] Failed for '{role}': {e}")
    results["Wellfound"] = wf_total

    # ── Monster ────────────────────────────────────────────────
    monster_total = 0
    for term, loc in MONSTER_SEARCHES:
        try:
            count = scraper.scrape_monster(search_term=term, location=loc)
            monster_total += count
        except Exception as e:
            logger.error(f"[Monster] Failed for '{term}': {e}")
    results["Monster"] = monster_total

    # ── Naukri ─────────────────────────────────────────────────
    naukri_total = 0
    for term, loc in NAUKRI_SEARCHES:
        try:
            count = scraper.scrape_naukri(search_term=term, location=loc)
            naukri_total += count
        except Exception as e:
            logger.error(f"[Naukri] Failed for '{term}': {e}")
    results["Naukri"] = naukri_total

    # ── RemoteOK (Public API) ──────────────────────────────────
    try:
        results["RemoteOK"] = scraper.scrape_remoteok()
    except Exception as e:
        logger.error(f"[RemoteOK] Task failed: {e}")
        results["RemoteOK"] = 0

    # ── Remotive (Public API) ──────────────────────────────────
    try:
        results["Remotive"] = scraper.scrape_remotive()
    except Exception as e:
        logger.error(f"[Remotive] Task failed: {e}")
        results["Remotive"] = 0

    db.close()

    grand_total = sum(results.values())
    logger.info(f"=== [Celery] Daily scraping complete. Results: {results}. Grand total: {grand_total} new jobs ===")
    return {"status": "success", "jobs_added": results, "total": grand_total}
