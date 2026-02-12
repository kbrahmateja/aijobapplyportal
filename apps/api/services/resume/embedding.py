from typing import List
from langchain_openai import OpenAIEmbeddings
from config import settings
import logging

class EmbeddingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # LangChain's OpenAIEmbeddings handles the OPENAI_API_KEY from env or passed arg.
        # We target the new efficient model: text-embedding-3-small
        if not settings.OPENAI_API_KEY:
            self.logger.warning("OPENAI_API_KEY not set. Using mock embeddings.")
            self.embeddings = None
        else:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY
            )

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text using OpenAI.
        Falls back to mock if API key is missing.
        """
        if self.embeddings:
            try:
                # remove newlines to reduce token usage/noise
                clean_text = text.replace("\n", " ")
                return self.embeddings.embed_query(clean_text)
            except Exception as e:
                self.logger.error(f"Error generating embedding: {e}. Falling back to mock.")
                # Fallback to mock behavior
                import random
                return [random.uniform(-1.0, 1.0) for _ in range(1536)]
        
        # Mock Fallback (for testing without costs)
        import random
        return [random.uniform(-1.0, 1.0) for _ in range(1536)]
