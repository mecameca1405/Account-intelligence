from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ..core.config import settings


class EmbeddingClient:
    """
    Encapsulates embedding generation logic.
    Uses Gemini embedding model via LangChain wrapper.
    """

    def __init__(self):
        self.model_name = settings.GEMINI_EMBEDDING_MODEL

        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model_name,
            google_api_key=settings.GEMINI_API_KEY
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        """
        return self._embeddings.embed_query(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """
        return self._embeddings.embed_documents(texts)