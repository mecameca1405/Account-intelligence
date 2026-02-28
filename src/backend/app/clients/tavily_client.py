from typing import List, Dict
from tavily import TavilyClient as TavilySDKClient
from app.core.config import settings


class TavilyClient:
    """
    Encapsulates Tavily web search functionality.
    """

    def __init__(self):
        self._client = TavilySDKClient(api_key=settings.TAVILY_API_KEY)

    def search(
        self,
        query: str,
        max_results: int = 3,
    ) -> List[Dict]:
        """
        Perform a web search query.
        Returns a list of result dictionaries.
        """

        response = self._client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_raw_content=True,
        )

        return response.get("results", [])