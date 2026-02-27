from ..clients.embedding_client import EmbeddingClient
from ..clients.pinecone_client import PineconeClient

embedding = EmbeddingClient()
pinecone = PineconeClient()

vector = embedding.embed_text("Test vector")

pinecone.upsert_vector(
    vector_id="test-1",
    values=vector,
    metadata={"type": "test"},
    namespace="test-namespace"
)

results = pinecone.similarity_search(
    query_vector=vector,
    namespace="test-namespace",
    top_k=3
)

print(results)