import os
import time
from services.browser.browser_manager import BrowserManager

COOKIES_FILE = "test_cookies.json"

def test_cookie_persistence():
    print("--- Testing Cookie Persistence ---")
    
    # Clean up previous test
    if os.path.exists(COOKIES_FILE):
        os.remove(COOKIES_FILE)

    print("\n1. First Session: Setting a Cookie")
    with BrowserManager(headless=True, cookies_path=COOKIES_FILE) as page:
        page.goto("https://example.com")
        
        # Set a dummy cookie
        context = page.context
        context.add_cookies([{
            "name": "TEST_SESSION",
            "value": "logged_in_user_123",
            "domain": "example.com",
            "path": "/"
        }])
        print("Cookie 'TEST_SESSION' set.")
        
        # Verify in memory
        current_cookies = context.cookies()
        print(f"Current Cookies in Memory: {[c['name'] for c in current_cookies]}")
        
    if os.path.exists(COOKIES_FILE):
        print(f"SUCCESS: {COOKIES_FILE} was created.")
    else:
        print(f"FAILURE: {COOKIES_FILE} was NOT created.")
        return

    print("\n2. Second Session: Checking if Cookie Persists")
    with BrowserManager(headless=True, cookies_path=COOKIES_FILE) as page:
        page.goto("https://example.com")
        
        cookies = page.context.cookies()
        found = False
        for c in cookies:
            if c["name"] == "TEST_SESSION" and c["value"] == "logged_in_user_123":
                found = True
                break
        
        if found:
            print("SUCCESS: Cookie 'TEST_SESSION' persisted!")
        else:
            print("FAILURE: Cookie NOT found in new session.")
            print(f"Found cookies: {[c['name'] for c in cookies]}")

if __name__ == "__main__":
    test_cookie_persistence()
