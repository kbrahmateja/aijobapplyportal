from services.resume.embedding import EmbeddingService
import os

def test_embedding_generation():
    print("Initializing EmbeddingService...")
    service = EmbeddingService()
    
    text = "Experienced Software Engineer with Python and AI skills."
    
    print(f"Generating embedding for: '{text}'")
    try:
        vector = service.generate_embedding(text)
        print(f"Success! Vector length: {len(vector)}")
        print(f"First 5 dimensions: {vector[:5]}")
        
        expected_dim = 1536
        if len(vector) == expected_dim:
            print(f"✅ Dimension check passed ({expected_dim})")
        else:
            print(f"❌ Dimension check failed. Expected {expected_dim}, got {len(vector)}")
            
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        print("Check if OPENAI_API_KEY is set in .env")

if __name__ == "__main__":
    test_embedding_generation()
