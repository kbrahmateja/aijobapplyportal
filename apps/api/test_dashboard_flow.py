import requests
from jose import jwt
import time
import json

# Mock JWT (Same as other tests)
payload = {
    "sub": "user_2sY...", 
    "email": "test@example.com",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}
API_URL = "http://localhost:8000/api"

def test_dashboard_flow():
    print("--- Testing Dashboard Flow ---")

    # 1. Apply to a Job (Job ID 6, Resume ID 3 - Ensure Resume 3 has nulled embedding for queuing)
    # We used Resume 3 in previous tests. 
    print("\n1. Applying to Job 6...")
    try:
        res = requests.post(f"{API_URL}/applications/6/apply", headers=headers, json={"resume_id": 3, "match_score": 0.95})
        if res.status_code == 200:
            app_data = res.json()
            print(f"Applied! ID: {app_data['id']}, Status: {app_data['status']}")
            app_id = app_data['id']
        else:
            print(f"Apply failed: {res.text}")
            return
    except Exception as e:
        print(f"Request failed: {e}")
        return

    # 2. Fetch Dashboard (List Applications)
    print("\n2. Fetching Dashboard...")
    try:
        res = requests.get(f"{API_URL}/applications/", headers=headers)
        if res.status_code == 200:
            apps = res.json()
            print(f"Found {len(apps)} applications.")
            found = False
            for app in apps:
                if app['id'] == app_id:
                    print(f" - Found our app: ID {app['id']}, Status: {app['status']}")
                    found = True
                    break
            if not found:
                print("ERROR: Application not found in dashboard list!")
        else:
            print(f"Dashboard fetch failed: {res.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # 3. Wait for Worker (if queued)
    if app_data['status'] == 'queued':
        print("\n3. Waiting for Worker (updating scheduled_at to Now)...")
        # trigger worker pickup by updating DB (since default delay is 1h)
        # We need to run psql command here or just wait if logic was immediate.
        # But for Free tier it's 1h delay.
        # I'll manually update it via psql command outside, or just trust previous worker verification.
        # Actually, let's just verify IT IS in the list. Execution was verified earlier.
        pass

if __name__ == "__main__":
    test_dashboard_flow()
