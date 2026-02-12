import requests
from jose import jwt
import time
import os

# Mock JWT
payload = {
    "sub": "user_2sY...", 
    "email": "test@example.com",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}
API_URL = "http://localhost:8000/api"

def create_dummy_pdf(filename="dummy.pdf"):
    with open(filename, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/Name /F1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000224 00000 n\n0000000312 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n406\n%%EOF")
    return filename

def test_resume_upload():
    print("--- Testing Resume Upload ---")
    filename = create_dummy_pdf()
    
    try:
        files = {'file': ('dummy.pdf', open(filename, 'rb'), 'application/pdf')}
        res = requests.post(f"{API_URL}/resumes/upload", headers=headers, files=files)
        
        if res.status_code == 200:
            print("Upload Success!")
            print(res.json())
        else:
            print(f"Upload Failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        os.remove(filename)

if __name__ == "__main__":
    test_resume_upload()
