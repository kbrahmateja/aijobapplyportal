from datetime import datetime, timezone
from models import Application, User, Job, Resume
from sqlalchemy.orm import Session
import logging
import time
from services.browser.browser_manager import BrowserManager

class ApplicationExecutionAgent:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def process_queue(self):
        """
        Polls for applications that are 'queued' and ready to be processed.
        """
        now = datetime.now(timezone.utc)
        
        # Fetch pending applications
        applications = self.db.query(Application).filter(
            Application.status == "queued",
            Application.scheduled_at <= now
        ).all()
        
        self.logger.info(f"Found {len(applications)} applications ready for processing.")
        
        for app in applications:
            try:
                self.process_application(app)
            except Exception as e:
                self.logger.error(f"Failed to process application {app.id}: {e}")
                app.status = "failed" # Or retry logic
                app.decision_reason = f"Execution failed: {str(e)}"
                self.db.commit()

    def process_application(self, application: Application):
        """
        Mock execution of the application.
        In real world, this would use Selenium/Playwright or API requests.
        """
        self.logger.info(f"Processing Application {application.id} for Job {application.job_id}...")
        
        job = self.db.query(Job).filter(Job.id == application.job_id).first()
        resume = self.db.query(Resume).filter(Resume.id == application.resume_id).first()
        user = self.db.query(User).filter(User.id == application.user_id).first()
        
        if not job or not resume or not user:
            raise ValueError("Job, Resume, or User missing")

        # Determine Strategy
        strategy = None
        browser = None
        
        try:
            # Using BrowserManager context
            # In production, cookies_path might be user-specific
            cookies_path = f"cookies_{user.id}.json"
            browser = BrowserManager(headless=False, cookies_path=cookies_path) 
            browser.start()
            
            if "linkedin.com" in job.url:
                from strategies.linkedin import LinkedInStrategy
                import os
                
                strategy = LinkedInStrategy(browser)
                
                # Login (MVP: Use Env Vars or Mock)
                # In real app, decrypt user credentials from DB
                username = os.getenv("LINKEDIN_USERNAME")
                password = os.getenv("LINKEDIN_PASSWORD")
                
                if username and password:
                    if not strategy.login(username, password):
                        raise Exception("Failed to login to LinkedIn")
                else:
                    self.logger.warning("No LinkedIn credentials found. Skipping login (hoping for cookies).")
            
            else:
                self.logger.info("No specific strategy for this URL. execution skipped (Mock).")
                time.sleep(1)
                # Fallback to mock for non-supported sites so we don't crash
                return

            # Prepare User Profile for Form Filler
            # We should extract this from Resume/User Profile in DB
            user_profile = {
                "first_name": getattr(user, 'first_name', "John"), 
                "last_name": getattr(user, 'last_name', "Doe"),
                "email": user.email,
                "phone": "123-456-7890", # Placeholder
                "resume_path": "dummy_resume.pdf" # Placeholder - needs real path logic
            }
            
            # Execute Application
            if strategy:
                success = strategy.apply_to_job(job.url, user_profile)
                
                if success:
                    application.status = "applied"
                    application.applied_at = datetime.now(timezone.utc)
                    application.decision_reason = "Successfully applied via LinkedIn Strategy"
                else:
                    application.status = "failed"
                    application.decision_reason = "Strategy execution returned False (e.g. element not found)"

                self.db.add(application)
                self.db.commit()
                self.logger.info(f"Application {application.id} finished with status: {application.status}")
            else:
                 self.logger.warning("No strategy selected, but fell through.")

        except Exception as e:
            self.logger.error(f"Execution Error: {e}")
            application.status = "failed"
            application.decision_reason = f"Error: {str(e)}"
            self.db.commit()
            
        finally:
            if browser:
                browser.stop()
