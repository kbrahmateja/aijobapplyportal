from database import SessionLocal
from services.browser.job_scraper import JobScraper
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ──────────────────────────────────────────────────────────────
# Job-search terms per source
# ──────────────────────────────────────────────────────────────
WWR_TERMS = ["python", "AI", "React", "Frontend", "DevOps", "Java"]

WELLFOUND_ROLES = [
    "software-engineer",
    "machine-learning-engineer",
    "frontend-engineer",
    "backend-engineer",
    "full-stack-engineer",
    "devops-engineer",
    "data-engineer",
]

MONSTER_SEARCHES = [
    ("python developer", "remote"),
    ("AI engineer", "remote"),
    ("react developer", "remote"),
    ("devops engineer", "remote"),
    ("java developer", "remote"),
    ("machine learning engineer", "remote"),
]

NAUKRI_SEARCHES = [
    ("python developer", ""),
    ("artificial intelligence", ""),
    ("react js developer", ""),
    ("devops engineer", ""),
    ("java developer", ""),
    ("machine learning engineer", ""),
    ("data engineer", ""),
]


def run_scraper():
    db = SessionLocal()
    scraper = JobScraper(db)
    total = 0

    print("\n" + "═" * 60)
    print("  AI Job Apply Portal — Multi-Source Job Scraper")
    print("═" * 60 + "\n")

    # ── 1. WeWorkRemotely ───────────────────────────────────────
    print("── WeWorkRemotely ──────────────────────────────────────")
    for term in WWR_TERMS:
        try:
            count = scraper.scrape_weworkremotely(search_term=term)
            print(f"  [{term}] → {count} new jobs")
            total += count
        except Exception as e:
            print(f"  [{term}] ERROR: {e}")

    # ── 2. Wellfound ────────────────────────────────────────────
    print("\n── Wellfound ───────────────────────────────────────────")
    for role in WELLFOUND_ROLES:
        try:
            count = scraper.scrape_wellfound(role=role)
            print(f"  [{role}] → {count} new jobs")
            total += count
        except Exception as e:
            print(f"  [{role}] ERROR: {e}")

    # ── 3. Monster ──────────────────────────────────────────────
    print("\n── Monster ─────────────────────────────────────────────")
    for term, loc in MONSTER_SEARCHES:
        try:
            count = scraper.scrape_monster(search_term=term, location=loc)
            print(f"  [{term} | {loc}] → {count} new jobs")
            total += count
        except Exception as e:
            print(f"  [{term}] ERROR: {e}")

    # ── 4. Naukri ───────────────────────────────────────────────
    print("\n── Naukri ──────────────────────────────────────────────")
    for term, loc in NAUKRI_SEARCHES:
        try:
            count = scraper.scrape_naukri(search_term=term, location=loc)
            print(f"  [{term}] → {count} new jobs")
            total += count
        except Exception as e:
            print(f"  [{term}] ERROR: {e}")

    # ── 5. RemoteOK (Public API) ────────────────────────────────
    print("\n── RemoteOK ─────────────────────────────────────────────")
    try:
        count = scraper.scrape_remoteok()
        print(f"  [all tags] → {count} new jobs")
        total += count
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 6. Remotive (Public API) ────────────────────────────────
    print("\n── Remotive ─────────────────────────────────────────────")
    try:
        count = scraper.scrape_remotive()
        print(f"  [all categories] → {count} new jobs")
        total += count
    except Exception as e:
        print(f"  ERROR: {e}")

    db.close()
    print("\n" + "═" * 60)
    print(f"  TOTAL NEW JOBS ADDED: {total}")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    run_scraper()
