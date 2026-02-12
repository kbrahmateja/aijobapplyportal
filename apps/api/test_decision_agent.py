import requests
from jose import jwt
import time

# Mock JWT
payload = {
    "sub": "user_2sY...", 
    "email": "test@example.com",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

def test_decision_agent():
    print("Testing Decision Agent...")
    
    # Needs a valid job ID and resume ID
    job_id = 6
    resume_id = 3 # ID from previous test
    
    url = f"http://localhost:8000/api/applications/{job_id}/apply"
    data = {
        "resume_id": resume_id,
        "match_score": 0.85 # High score to pass filters
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.text)
            
        # Test 2: Low Score (Should be rejected for Free Tier)
        print("\n--- Test 2: Low Match Score (0.5) ---")
        data["match_score"] = 0.5
        # We need a different job ID to avoid "already exists" check, or just fail expectedly
        # Let's try same job, it might return existing.
        # Actually, for testing rejection, we should use a new job or clear DB. 
        # But let's see what happens.
        
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print("Response:", response.json())
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_decision_agent()
