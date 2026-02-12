from strategies.base_strategy import JobApplicationStrategy
from agents.form_filler import FormFiller
import time

class LinkedInStrategy(JobApplicationStrategy):
    def login(self, username: str, password: str) -> bool:
        page = self.browser_manager.page
        if not page:
            raise Exception("Browser page not initialized")

        try:
            self.logger.info("Navigating to LinkedIn Login...")
            page.goto("https://www.linkedin.com/login")
            
            # Check if already logged in (cookie persistence)
            if "feed" in page.url:
                self.logger.info("Already logged in!")
                return True

            page.fill("#username", username)
            page.fill("#password", password)
            page.click("button[type='submit']")
            
            page.wait_for_url("**/feed/**", timeout=15000)
            self.logger.info("Successfully logged in to LinkedIn.")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False

    def apply_to_job(self, job_url: str, user_profile: dict) -> bool:
        page = self.browser_manager.page
        filler = FormFiller(page)
        
        try:
            self.logger.info(f"Navigating to Job: {job_url}")
            page.goto(job_url)
            
            # 1. Click "Easy Apply"
            # LinkedIn DOM structures vary wildly. This is a best-effort MVP starter.
            easy_apply_btn = page.locator("button.jobs-apply-button--top-card")
            
            if easy_apply_btn.count() == 0:
                self.logger.warning("Easy Apply button not found. Might be 'Apply' (external) or already applied.")
                return False
                
            easy_apply_btn.first.click()
            self.logger.info("Clicked Easy Apply")
            
            # 2. Handle Modal Steps
            # Loop through "Next" buttons until "Submit" or "Review"
            max_steps = 10
            for _ in range(max_steps):
                time.sleep(2) # Human delay
                
                # Check for Submit
                submit_btn = page.get_by_role("button", name="Submit application")
                if submit_btn.count() > 0:
                    self.logger.info("Found Submit Button!")
                    # In MVP we might pause here or submit if confident
                    # submit_btn.click() 
                    return True
                
                # Fill common visible fields
                filler.fill_text_field("Phone", user_profile.get("phone", ""))
                filler.fill_text_field("Mobile", user_profile.get("phone", ""))
                
                # Check for Next
                next_btn = page.get_by_role("button", name="Next")
                if next_btn.count() > 0:
                    next_btn.click()
                    continue
                    
                # If neither, maybe Review?
                review_btn = page.get_by_role("button", name="Review")
                if review_btn.count() > 0:
                    review_btn.click()
                    continue
                    
                self.logger.info("No obvious buttons found. Modal might be stuck or finished.")
                break
                
            return False

        except Exception as e:
            self.logger.error(f"Application failed: {e}")
            return False
