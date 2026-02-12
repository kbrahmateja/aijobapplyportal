import requests
from jose import jwt
import time

# Mock JWT for Dev Mode (since CLERK_ISSUER is empty by default)
payload = {
    "sub": "user_2sY...", 
    "email": "test@example.com",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256") # Algorithm doesn't matter for unverified decode

headers = {
    "Authorization": f"Bearer {token}"
}

def test_upload_protected():
    print("Testing Protected Upload Endpoint...")
    url = "http://localhost:8000/api/resumes/upload"
    
    # create a dummy pdf
    with open("valid_resume.pdf", "rb") as f:
        files = {"file": ("resume.pdf", f, "application/pdf")}
        try:
            response = requests.post(url, headers=headers, files=files)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("Success ID:", data["id"])
                print("Structured Data Preview:", str(data.get("data", {}))[:200] + "...")
                return data["id"]
            else:
                print("Error:", response.text)
        except Exception as e:
            print(f"Request failed: {e}")
            
def test_matching_protected(resume_id):
    if not resume_id:
        return
        
    print(f"\nTesting Protected Matching Endpoint for Resume {resume_id}...")
    url = f"http://localhost:8000/api/resumes/{resume_id}/matches"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Found {len(response.json())} matches")
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    resume_id = test_upload_protected()
    test_matching_protected(resume_id)
