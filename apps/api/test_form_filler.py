import os
import time
from services.browser.browser_manager import BrowserManager
from agents.form_filler import FormFiller

def test_form_filler():
    print("--- Testing Form Filler Agent ---")
    
    # Path to local dummy form
    cwd = os.getcwd()
    file_path = f"file://{cwd}/tests/dummy_form.html"
    
    # Create a dummy resume file for upload test
    with open("dummy_resume.pdf", "w") as f:
        f.write("Dummy PDF Content")
    
    try:
        with BrowserManager(headless=False) as page:
            print(f"Navigating to: {file_path}")
            page.goto(file_path)
            
            filler = FormFiller(page)
            
            # 1. Fill Text Fields (heuristics)
            print("Filling Name...")
            filler.fill_text_field("First Name", "John")
            filler.fill_text_field("Last Name", "Doe")
            
            print("Filling Email...")
            filler.fill_text_field("Email", "john.doe@example.com")
            
            print("Filling LinkedIn...")
            filler.fill_text_field("LinkedIn", "https://linkedin.com/in/johndoe")
            
            # 2. Upload File
            print("Uploading Resume...")
            filler.upload_file("Resume", os.path.abspath("dummy_resume.pdf"))
            
            # 3. Submit
            print("Clicking Submit...")
            # Handling alert dialog that appears on submit
            def handle_dialog(dialog):
                print(f"Alert Detected: {dialog.message}")
                dialog.accept()
                
            page.on("dialog", handle_dialog)
            filler.click_button("Submit Application")
            
            print("Waiting for visual verification...")
            time.sleep(3)
            print("Test Complete.")
            
    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        if os.path.exists("dummy_resume.pdf"):
            os.remove("dummy_resume.pdf")

if __name__ == "__main__":
    test_form_filler()
