import logging
from database import SessionLocal
from services.browser.job_scraper import JobScraper

logger = logging.getLogger(__name__)

# ── WeWorkRemotely ────────────────────────────────────────────
WWR_TERMS = ["python", "AI", "React", "Frontend", "DevOps", "Java"]

# ── Wellfound ─────────────────────────────────────────────────
WELLFOUND_ROLES = [
    "software-engineer",
    "machine-learning-engineer",
    "frontend-engineer",
    "backend-engineer",
    "full-stack-engineer",
    "devops-engineer",
]

# ── Monster ───────────────────────────────────────────────────
MONSTER_SEARCHES = [
    ("python developer", "remote"),
    ("AI engineer", "remote"),
    ("react developer", "remote"),
    ("devops engineer", "remote"),
    ("machine learning engineer", "remote"),
]

# ── Naukri ────────────────────────────────────────────────────
NAUKRI_SEARCHES = [
    ("python developer", ""),
    ("artificial intelligence", ""),
    ("react js developer", ""),
    ("devops engineer", ""),
    ("machine learning engineer", ""),
    ("data engineer", ""),
]
