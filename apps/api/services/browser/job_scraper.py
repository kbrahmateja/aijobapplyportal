import logging
import time
import random
from datetime import datetime
from services.browser.browser_manager import BrowserManager
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from models import Job
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self._pending = 0  # track staged rows

    def _random_delay(self, min_s=1.5, max_s=3.5):
        """Human-speed random delay between actions."""
        time.sleep(random.uniform(min_s, max_s))

    def _save_job(self, title, company, location, description, url, source, posted_at=None):
        """
        Insert a Job row using ON CONFLICT (url) DO NOTHING — 100% safe to call
        even if the URL already exists. Returns True if a new row was actually inserted.
        """
        if not title or not url:
            return False
        try:
            stmt = pg_insert(Job.__table__).values(
                title=title,
                company=company or "Unknown",
                location=location or "Remote",
                description=description or f"Job scraped from {source}.",
                url=url,
                source=source,
                posted_at=posted_at or datetime.utcnow(),
            ).on_conflict_do_nothing(index_elements=["url"])
            result = self.db.execute(stmt)
            inserted = result.rowcount > 0
            if inserted:
                self.logger.info(f"[{source}] Added: {title} @ {company}")
                self._pending += 1
            return inserted
        except Exception as e:
            self.logger.error(f"[{source}] _save_job error for '{url}': {e}")
            self.db.rollback()
            return False

    def _commit(self):
        if self._pending > 0:
            try:
                self.db.commit()
                self._pending = 0
            except Exception as e:
                self.db.rollback()
                self._pending = 0
                self.logger.error(f"DB commit failed: {e}")

    # ──────────────────────────────────────────────
    # 1. WeWorkRemotely (original)
    # ──────────────────────────────────────────────
    def scrape_weworkremotely(self, search_term: str = "python"):
        """Scrapes WeWorkRemotely for jobs matching search_term."""
        url = f"https://weworkremotely.com/remote-jobs/search?term={search_term}"
        self.logger.info(f"[WeWorkRemotely] Scraping: {url}")
        count = 0

        try:
            with BrowserManager(headless=True) as page:
                page.goto(url)
                page.wait_for_selector(".jobs-container", timeout=15000)
                soup = BeautifulSoup(page.content(), "html.parser")

                for item in soup.select("section.jobs article ul li"):
                    if "view-all" in item.get("class", []):
                        continue
                    try:
                        title_elem = item.select_one(".new-listing__header__title")
                        company_elem = item.select_one(".new-listing__company-name")
                        region_elem = item.select_one(".new-listing__company-headquarters")
                        link_elem = item.select_one("a.listing-link--unlocked") or item.select_one("a")

                        if not title_elem or not company_elem or not link_elem:
                            continue

                        href = link_elem["href"]
                        if not href.startswith("http"):
                            href = f"https://weworkremotely.com{href}"

                        added = self._save_job(
                            title=title_elem.get_text(strip=True),
                            company=company_elem.get_text(strip=True),
                            location=region_elem.get_text(strip=True) if region_elem else "Remote",
                            description=f"Scraped from WeWorkRemotely. Search: {search_term}",
                            url=href,
                            source="WeWorkRemotely",
                        )
                        if added:
                            count += 1
                    except Exception as e:
                        self.logger.error(f"[WeWorkRemotely] Item parse error: {e}")

                self._commit()
        except Exception as e:
            self.logger.error(f"[WeWorkRemotely] Scraper error: {e}")

        self.logger.info(f"[WeWorkRemotely] Done. Added {count} jobs for '{search_term}'.")
        return count

    # ──────────────────────────────────────────────
    # 2. Wellfound (formerly AngelList Talent)
    # ──────────────────────────────────────────────
    def scrape_wellfound(self, role: str = "software-engineer", location: str = "remote"):
        """
        Scrapes Wellfound job listings.
        Primary URL: https://wellfound.com/jobs?role=<role>&remote=true
        Fallback URL: https://wellfound.com/role/r/<role>
        Falls back gracefully on anti-bot / sign-up walls.
        """
        role_slug = role.lower().replace(" ", "-")
        # Use the jobs search page which has less aggressive gating
        primary_url = f"https://wellfound.com/jobs?role={role_slug}&remote=true"
        fallback_url = f"https://wellfound.com/role/r/{role_slug}"
        self.logger.info(f"[Wellfound] Scraping: {primary_url}")
        count = 0

        for attempt_url in [primary_url, fallback_url]:
            try:
                with BrowserManager(headless=True) as page:
                    page.goto(attempt_url, timeout=30000)
                    self._random_delay(3, 5)

                    # Dismiss modals / cookie banners if present
                    try:
                        page.keyboard.press("Escape")
                    except Exception:
                        pass

                    content = page.content()

                    # Detect hard sign-up wall (no job cards, only auth prompt)
                    no_jobs = "job-listings" not in content and 'data-test="JobSearchResult"' not in content
                    hard_wall = ("Create a free account" in content or "Sign up to see" in content) and no_jobs
                    if hard_wall:
                        self.logger.warning(f"[Wellfound] Sign-up wall on {attempt_url}. Trying fallback...")
                        continue

                    # Wait for cards
                    try:
                        page.wait_for_selector(
                            '[data-test="JobSearchResult"], div[class*="JobListing"], [data-test="StartupResult"]',
                            timeout=10000
                        )
                    except Exception:
                        self.logger.warning(f"[Wellfound] No card selector on {attempt_url}. Parsing anyway.")

                    soup = BeautifulSoup(page.content(), "html.parser")

                    job_cards = (
                        soup.select('[data-test="JobSearchResult"]') or
                        soup.select("div[class*='JobListing']") or
                        soup.select('[data-test="StartupResult"]') or
                        soup.select("div[class*='styles_result']")
                    )

                    self.logger.info(f"[Wellfound] Found {len(job_cards)} cards on {attempt_url}.")

                    for card in job_cards:
                        try:
                            title_elem = (
                                card.select_one("a[class*='jobTitle']") or
                                card.select_one("h2 a") or
                                card.select_one("h3 a") or
                                card.select_one("a[href*='/jobs/']")
                            )
                            company_elem = (
                                card.select_one("a[class*='startup']") or
                                card.select_one("a[href*='/company/']") or
                                card.select_one("span[class*='company']")
                            )
                            location_elem = (
                                card.select_one("span[class*='location']") or
                                card.select_one("div[class*='location']")
                            )
                            link_elem = card.select_one("a[href*='/jobs/']") or card.select_one("a")

                            if not title_elem or not link_elem:
                                continue

                            href = link_elem.get("href", "")
                            if not href.startswith("http"):
                                href = f"https://wellfound.com{href}"

                            added = self._save_job(
                                title=title_elem.get_text(strip=True),
                                company=company_elem.get_text(strip=True) if company_elem else "Startup",
                                location=location_elem.get_text(strip=True) if location_elem else "Remote",
                                description=f"Scraped from Wellfound. Role: {role}",
                                url=href,
                                source="Wellfound",
                            )
                            if added:
                                count += 1
                        except Exception as e:
                            self.logger.error(f"[Wellfound] Card parse error: {e}")

                    self._commit()
                    break  # Success — no need to try fallback URL

            except Exception as e:
                self.logger.error(f"[Wellfound] Scraper error on {attempt_url}: {e}")

        self.logger.info(f"[Wellfound] Done. Added {count} jobs for role '{role}'.")
        return count

    # ──────────────────────────────────────────────
    # 3. Monster
    # ──────────────────────────────────────────────
    def scrape_monster(self, search_term: str = "python developer", location: str = "remote"):
        """
        Scrapes Monster.com for job listings.
        URL: https://www.monster.com/jobs/search?q=<term>&where=<location>
        """
        query = search_term.replace(" ", "+")
        loc = location.replace(" ", "+")
        url = f"https://www.monster.com/jobs/search?q={query}&where={loc}"
        self.logger.info(f"[Monster] Scraping: {url}")
        count = 0

        try:
            with BrowserManager(headless=True) as page:
                page.goto(url, timeout=30000)
                self._random_delay(2, 4)

                # Monster loads cards via JS; wait for job card container
                try:
                    page.wait_for_selector("[data-testid='jobCard'], .job-cardstyle__JobCardComponent, .card-content", timeout=15000)
                except Exception:
                    self.logger.warning("[Monster] Job cards selector timed out. Attempting parse anyway.")

                # Scroll to load more results
                for _ in range(3):
                    page.evaluate("window.scrollBy(0, 800)")
                    self._random_delay(1, 2)

                soup = BeautifulSoup(page.content(), "html.parser")

                # Try multiple selector strategies for Monster
                job_cards = (
                    soup.select("[data-testid='jobCard']") or
                    soup.select(".job-cardstyle__JobCardComponent") or
                    soup.select("article.card") or
                    soup.select(".card-content")
                )

                self.logger.info(f"[Monster] Found {len(job_cards)} potential job cards.")

                for card in job_cards:
                    try:
                        # Title
                        title_elem = (
                            card.select_one("[data-testid='jobTitle']") or
                            card.select_one("h2.title") or
                            card.select_one("a.job-title") or
                            card.select_one("h2") or
                            card.select_one("h3")
                        )
                        # Company
                        company_elem = (
                            card.select_one("[data-testid='company']") or
                            card.select_one(".company") or
                            card.select_one("div[class*='company']") or
                            card.select_one("span[class*='company']")
                        )
                        # Location
                        location_elem = (
                            card.select_one("[data-testid='jobLocation']") or
                            card.select_one(".location") or
                            card.select_one("div[class*='location']")
                        )
                        # Link
                        link_elem = card.select_one("a[href*='/job-openings/']") or card.select_one("a")

                        if not title_elem or not link_elem:
                            continue

                        href = link_elem.get("href", "")
                        if not href.startswith("http"):
                            href = f"https://www.monster.com{href}"

                        # Filter out non-job links
                        if "monster.com" not in href and not href.startswith("/"):
                            continue

                        added = self._save_job(
                            title=title_elem.get_text(strip=True),
                            company=company_elem.get_text(strip=True) if company_elem else "Company",
                            location=location_elem.get_text(strip=True) if location_elem else location,
                            description=f"Scraped from Monster. Search: {search_term}",
                            url=href,
                            source="Monster",
                        )
                        if added:
                            count += 1
                    except Exception as e:
                        self.logger.error(f"[Monster] Card parse error: {e}")

                self._commit()
        except Exception as e:
            self.logger.error(f"[Monster] Scraper error: {e}")

        self.logger.info(f"[Monster] Done. Added {count} jobs for '{search_term}'.")
        return count

    # ──────────────────────────────────────────────
    # 4. Naukri
    # ──────────────────────────────────────────────
    def scrape_naukri(self, search_term: str = "python developer", location: str = ""):
        """
        Scrapes Naukri.com for tech job listings (India-focused).
        URL: https://www.naukri.com/<search-slug>-jobs[/<location>]
        """
        slug = search_term.lower().replace(" ", "-")
        loc_slug = location.lower().replace(" ", "-") if location else ""
        url = f"https://www.naukri.com/{slug}-jobs"
        if loc_slug:
            url += f"-in-{loc_slug}"
        self.logger.info(f"[Naukri] Scraping: {url}")
        count = 0

        try:
            with BrowserManager(headless=True) as page:
                page.goto(url, timeout=30000)
                self._random_delay(2, 5)

                # Naukri uses SSR; wait for article list
                try:
                    page.wait_for_selector(".jobTupleHeader, article.jobTuple, .srp-jobtuple-wrapper", timeout=15000)
                except Exception:
                    self.logger.warning("[Naukri] Job tuple selector timed out. Attempting parse anyway.")

                soup = BeautifulSoup(page.content(), "html.parser")

                # Naukri selectors (SSR rendered)
                job_cards = (
                    soup.select("article.jobTuple") or
                    soup.select(".srp-jobtuple-wrapper") or
                    soup.select(".jobTupleHeader")
                )

                self.logger.info(f"[Naukri] Found {len(job_cards)} potential job cards.")

                for card in job_cards:
                    try:
                        # Title
                        title_elem = (
                            card.select_one(".title a") or
                            card.select_one("a.title") or
                            card.select_one(".jobTitle a") or
                            card.select_one("a[class*='title']")
                        )
                        # Company
                        company_elem = (
                            card.select_one(".companyInfo a") or
                            card.select_one("a.subTitle") or
                            card.select_one(".comp-name")
                        )
                        # Location
                        location_elem = (
                            card.select_one(".locWdth") or
                            card.select_one(".location span") or
                            card.select_one("li.location")
                        )

                        if not title_elem:
                            continue

                        href = title_elem.get("href", "")
                        if not href:
                            continue
                        if not href.startswith("http"):
                            href = f"https://www.naukri.com{href}"

                        added = self._save_job(
                            title=title_elem.get_text(strip=True),
                            company=company_elem.get_text(strip=True) if company_elem else "Company",
                            location=location_elem.get_text(strip=True) if location_elem else (location or "India"),
                            description=f"Scraped from Naukri. Search: {search_term}",
                            url=href,
                            source="Naukri",
                        )
                        if added:
                            count += 1
                    except Exception as e:
                        self.logger.error(f"[Naukri] Card parse error: {e}")

                self._commit()
        except Exception as e:
            self.logger.error(f"[Naukri] Scraper error: {e}")

        self.logger.info(f"[Naukri] Done. Added {count} jobs for '{search_term}'.")
        return count

    # ──────────────────────────────────────────────
    # 5. RemoteOK (Public JSON API — no auth needed)
    # ──────────────────────────────────────────────
    def scrape_remoteok(self, tags: list = None):
        """
        Fetches jobs from RemoteOK's public JSON API.
        API: https://remoteok.com/api?tags=<tag>
        No authentication required. Results include title, company, location, tags, URL.
        """
        import httpx

        if tags is None:
            tags = ["python", "javascript", "react", "devops", "ai", "java", "golang"]

        count = 0
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; JobPortalBot/1.0)",
            "Accept": "application/json",
        }

        for tag in tags:
            url = f"https://remoteok.com/api?tags={tag}"
            self.logger.info(f"[RemoteOK] Fetching: {url}")
            try:
                response = httpx.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()

                # First element is metadata/notice, rest are jobs
                jobs = [item for item in data if isinstance(item, dict) and item.get("position")]

                self.logger.info(f"[RemoteOK] Found {len(jobs)} jobs for tag '{tag}'.")

                for job in jobs:
                    try:
                        title = job.get("position", "")
                        company = job.get("company", "Unknown")
                        location = job.get("location", "") or "Remote"
                        job_url = job.get("url", "")
                        if not job_url:
                            slug = job.get("slug", "")
                            job_url = f"https://remoteok.com/remote-jobs/{slug}" if slug else ""
                        description = job.get("description", "") or f"Scraped from RemoteOK. Tags: {', '.join(job.get('tags', [tag]))}"

                        # Strip HTML from description
                        if "<" in description:
                            soup = BeautifulSoup(description, "html.parser")
                            description = soup.get_text(separator=" ", strip=True)[:2000]

                        # Parse date
                        posted_at = None
                        date_str = job.get("date", "")
                        if date_str:
                            try:
                                from datetime import timezone
                                posted_at = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                            except Exception:
                                posted_at = datetime.utcnow()

                        added = self._save_job(
                            title=title,
                            company=company,
                            location=location,
                            description=description,
                            url=job_url,
                            source="RemoteOK",
                            posted_at=posted_at,
                        )
                        if added:
                            count += 1
                    except Exception as e:
                        self.logger.error(f"[RemoteOK] Job parse error: {e}")

                self._commit()
                self._random_delay(1, 2)  # Be polite to the API

            except Exception as e:
                self.logger.error(f"[RemoteOK] API error for tag '{tag}': {e}")

        self.logger.info(f"[RemoteOK] Done. Added {count} total new jobs.")
        return count

    # ──────────────────────────────────────────────
    # 6. Remotive (Public JSON API — no auth needed)
    # ──────────────────────────────────────────────
    def scrape_remotive(self, categories: list = None):
        """
        Fetches jobs from Remotive's public JSON API.
        API: https://remotive.com/api/remote-jobs?category=<category>
        No authentication required. Returns rich structured job data.
        """
        import httpx

        if categories is None:
            categories = [
                "software-dev",
                "data",
                "devops-sysadmin",
                "product",
                "qa",
            ]

        count = 0

        for category in categories:
            url = f"https://remotive.com/api/remote-jobs?category={category}&limit=50"
            self.logger.info(f"[Remotive] Fetching: {url}")
            try:
                response = httpx.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])

                self.logger.info(f"[Remotive] Found {len(jobs)} jobs in category '{category}'.")

                for job in jobs:
                    try:
                        title = job.get("title", "")
                        company = job.get("company_name", "Unknown")
                        location = job.get("candidate_required_location", "Remote") or "Remote"
                        job_url = job.get("url", "")
                        description = job.get("description", "") or f"Scraped from Remotive. Category: {category}"

                        # Strip HTML from description
                        if "<" in description:
                            soup = BeautifulSoup(description, "html.parser")
                            description = soup.get_text(separator=" ", strip=True)[:2000]

                        # Parse date
                        posted_at = None
                        date_str = job.get("publication_date", "")
                        if date_str:
                            try:
                                posted_at = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                            except Exception:
                                posted_at = datetime.utcnow()

                        added = self._save_job(
                            title=title,
                            company=company,
                            location=location,
                            description=description,
                            url=job_url,
                            source="Remotive",
                            posted_at=posted_at,
                        )
                        if added:
                            count += 1
                    except Exception as e:
                        self.logger.error(f"[Remotive] Job parse error: {e}")

                self._commit()
                self._random_delay(0.5, 1)

            except Exception as e:
                self.logger.error(f"[Remotive] API error for category '{category}': {e}")

        self.logger.info(f"[Remotive] Done. Added {count} total new jobs.")
        return count
