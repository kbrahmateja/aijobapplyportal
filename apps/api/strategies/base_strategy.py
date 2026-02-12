from abc import ABC, abstractmethod
from services.browser.browser_manager import BrowserManager
from agents.form_filler import FormFiller
import logging

class JobApplicationStrategy(ABC):
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Logs into the platform. Returns True if successful.
        """
        pass

    @abstractmethod
    def apply_to_job(self, job_url: str, user_profile: dict) -> bool:
        """
        Navigates to the job URL and attempts to apply.
        user_profile should contain: first_name, last_name, email, phone, resume_path, etc.
        """
        pass
