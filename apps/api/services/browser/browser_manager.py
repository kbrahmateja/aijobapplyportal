import logging
import random
import os
from playwright.sync_api import sync_playwright, Page, BrowserContext

class BrowserManager:
    def __init__(self, headless: bool = False, cookies_path: str = None):
        self.headless = headless
        self.cookies_path = cookies_path
        self.logger = logging.getLogger(__name__)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self) -> Page:
        self.start()
        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cookies_path and self.context:
            try:
                self.save_cookies(self.cookies_path)
            except Exception as e:
                self.logger.error(f"Failed to auto-save cookies: {e}")
        self.stop()

    def start(self):
        self.logger.info(f"Starting Browser (Headless={self.headless})...")
        self.playwright = sync_playwright().start()
        
        # Launch options for "Stealth" (basic for now)
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        
        # Load cookies if exist
        storage_state = None
        if self.cookies_path and os.path.exists(self.cookies_path):
            self.logger.info(f"Loading cookies from {self.cookies_path}")
            storage_state = self.cookies_path

        # Create Context
        self.context = self.browser.new_context(
            storage_state=storage_state,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        self.page = self.context.new_page()
        
        # Add basic stealth scripts
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.logger.info("Browser started successfully.")

    def save_cookies(self, path: str):
        """Saves current cookies/storage state to a file."""
        if self.context:
            self.context.storage_state(path=path)
            self.logger.info(f"Cookies saved to {path}")

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser stopped.")
