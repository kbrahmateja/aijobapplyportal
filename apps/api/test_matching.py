import requests

def test_matching():
    # Assuming resume ID 1 exists (from previous test_upload.py run)
    resume_id = 1
    url = f"http://localhost:8000/api/resumes/{resume_id}/matches"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            matches = response.json()
            print(f"Found {len(matches)} matches:")
            for match in matches:
                print(f"- {match['title']} at {match['company']} (Score: {match['similarity']:.4f})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_matching()
