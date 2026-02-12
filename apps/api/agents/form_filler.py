import logging
from services.browser.browser_manager import BrowserManager
from playwright.sync_api import Page, Locator

class FormFiller:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    def fill_text_field(self, label_pattern: str, value: str):
        """
        Fills a text input by finding a label that matches the pattern.
        """
        try:
            # Strategies to find the input:
            # 1. By Label Text
            input_locator = self.page.get_by_label(label_pattern, exact=False)
            if input_locator.count() > 0:
                input_locator.first.fill(value)
                self.logger.info(f"Filled '{label_pattern}' with '{value}' (via label)")
                return True

            # 2. By Placeholder
            input_locator = self.page.get_by_placeholder(label_pattern, exact=False)
            if input_locator.count() > 0:
                input_locator.first.fill(value)
                self.logger.info(f"Filled '{label_pattern}' with '{value}' (via placeholder)")
                return True
                
            self.logger.warning(f"Could not find field for '{label_pattern}'")
            return False
            
        except Exception as e:
            self.logger.error(f"Error filling '{label_pattern}': {e}")
            return False

    def upload_file(self, label_pattern: str, file_path: str):
        """
        Uploads a file to an input found by label/text.
        """
        try:
            # Find file input directly if possible
            file_input = self.page.locator("input[type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(file_path)
                self.logger.info(f"Uploaded file to generic file input")
                return True
                
            self.logger.warning(f"Could not find file input for '{label_pattern}'")
            return False
            
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return False
            
    def click_button(self, label_pattern: str):
        """
        Clicks a button with specific text.
        """
        try:
            # Case insensitive regex for button text
            import re
            regex = re.compile(label_pattern, re.IGNORECASE)
            
            button = self.page.get_by_role("button", name=regex)
            if button.count() > 0:
                button.first.click()
                self.logger.info(f"Clicked button '{label_pattern}'")
                return True
                
            # Fallback to text
            button = self.page.get_by_text(regex)
            if button.count() > 0:
                button.first.click()
                self.logger.info(f"Clicked text '{label_pattern}'")
                return True

            self.logger.warning(f"Could not find button '{label_pattern}'")
            return False
            
        except Exception as e:
            self.logger.error(f"Error clicking button '{label_pattern}': {e}")
            return False
