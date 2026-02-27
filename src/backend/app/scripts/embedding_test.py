from ..clients.embedding_client import EmbeddingClient

client = EmbeddingClient()
vector = client.embed_text("Hello world")
print(len(vector))