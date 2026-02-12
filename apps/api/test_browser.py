from services.browser.browser_manager import BrowserManager
import time

def test_browser_launch():
    print("--- Testing Browser Launch (Headed) ---")
    
    # Run in HEADED mode to see it
    try:
        with BrowserManager(headless=False) as page:
            print("Browser launched!")
            
            print("Navigating to example.com...")
            page.goto("https://example.com")
            
            title = page.title()
            print(f"Page Title: {title}")
            
            # Take a screenshot
            page.screenshot(path="browser_test.png")
            print("Screenshot saved to browser_test.png")
            
            print("Waiting 5 seconds for visual verification...")
            time.sleep(5)
            
            if "Example Domain" in title:
                print("SUCCESS: Browser verification passed.")
            else:
                print("FAILURE: Unexpected title.")
                
    except Exception as e:
        print(f"Browser Test Failed: {e}")

if __name__ == "__main__":
    test_browser_launch()
