from ..clients.tavily_client import TavilyClient

client = TavilyClient()

results = client.search("Kavak company financial performance")

print(len(results))
print(results[0].keys())