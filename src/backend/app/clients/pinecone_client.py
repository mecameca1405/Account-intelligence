from typing import List, Dict, Any
from pinecone import Pinecone
from app.core.config import settings


class PineconeClient:
    """
    Encapsulates all interactions with Pinecone vector database.
    """

    def __init__(self):
        self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self._index = self._pc.Index(settings.PINECONE_INDEX_NAME)

    def upsert_vector(
        self,
        vector_id: str,
        values: List[float],
        metadata: Dict[str, Any],
        namespace: str,
    ) -> None:
        """
        Insert or update a single vector in a namespace.
        """
        self._index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": values,
                    "metadata": metadata,
                }
            ],
            namespace=namespace,
        )

    def upsert_batch(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str,
    ) -> None:
        """
        Insert multiple vectors at once.
        Each vector dict must contain: id, values, metadata
        """
        self._index.upsert(
            vectors=vectors,
            namespace=namespace,
        )

    def similarity_search(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search inside a namespace.
        """
        response = self._index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
        )

        return response.get("matches", [])