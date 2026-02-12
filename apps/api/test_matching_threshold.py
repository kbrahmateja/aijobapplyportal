import requests
from jose import jwt
import time

# Mock JWT for Dev Mode
payload = {
    "sub": "user_2sY...", 
    "email": "test@example.com",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

def test_matching_threshold():
    # Assuming resume ID 3 exists from previous test_auth.py run (or we can use 1/2 if they have embed)
    # We'll use the one from test_auth which was ID 3
    resume_id = 3 
    
    print(f"Testing Matching Thresholds for Resume {resume_id}...")
    
    # Test 1: No Threshold (Should return all/any)
    print("\n--- Test 1: No Threshold (min_similarity=0) ---")
    url_all = f"http://localhost:8000/api/resumes/{resume_id}/matches?limit=5"
    resp_all = requests.get(url_all, headers=headers)
    if resp_all.status_code == 200:
        matches = resp_all.json()
        print(f"Found {len(matches)} matches.")
        if matches:
            best_score = matches[0]['similarity']
            print(f"Best Score: {best_score}")
            
            # Test 2: High Threshold (Should likely filter all out if using random embeddings)
            # Random embeddings usually have very low cosine similarity (near 0)
            threshold = 0.8
            print(f"\n--- Test 2: High Threshold (min_similarity={threshold}) ---")
            url_high = f"http://localhost:8000/api/resumes/{resume_id}/matches?limit=5&min_similarity={threshold}"
            resp_high = requests.get(url_high, headers=headers)
            matches_high = resp_high.json()
            print(f"Found {len(matches_high)} matches.")
            
            # Test 3: Low Threshold (Should filtering some if possible, or just work)
            threshold_low = -0.5 # Cosine sim can be negative. 
            print(f"\n--- Test 3: Low Threshold (min_similarity={threshold_low}) ---")
            url_low = f"http://localhost:8000/api/resumes/{resume_id}/matches?limit=5&min_similarity={threshold_low}"
            resp_low = requests.get(url_low, headers=headers)
            matches_low = resp_low.json()
            print(f"Found {len(matches_low)} matches.")
            
    else:
        print("Error:", resp_all.text)

if __name__ == "__main__":
    test_matching_threshold()
