import os
from typing import Literal, List, Dict, Union, Any
from langchain.tools import tool
from tavily import TavilyClient
from src.config.settings import settings
from src.logging.logging import setup_logger

logger = setup_logger(__file__)


class WebSearchService:
    def __init__(self):
        # Initialize the client inside the class
        self.api_key = settings.tavily_api_key
        if not self.api_key:
             # Fallback or error handling if key is missing
             raise ValueError("TAVILY_API_KEY is not set in environment variables.")
        self.client = TavilyClient(api_key=self.api_key)

    def execute(self, query: str, country: str, max_results: int, search_depth: str, topic: str):
        return self._perform_search(query, country, max_results, search_depth, topic)

    def _perform_search(self, query, country, max_results, search_depth, topic):
        try:
            # Preserving exact logic from original function
            if topic == "general":
                response = self.client.search(
                    query = query,
                    search_depth = search_depth,
                    topic = topic,
                    country =  country,
                    max_results=max_results
                )
            else:
                # Original logic did not pass 'country' for non-general topics
                response = self.client.search(
                    query=query,
                    search_depth=search_depth,
                    topic=topic,
                    max_results=max_results
                )
            return response.get("results", [])

        except Exception as e:
            return f"Error performing search: {str(e)}"

# Initialize the Service
web_search_service = WebSearchService()

@tool("Web_Search_Tool")
def web_search_tool(
    query: str, 
    country: str = "china", 
    max_results: int = 5,
    search_depth: Literal["basic", "advanced"] = "advanced",
    topic: Literal["general", "news"] = "general"
) -> Union[List[Dict[str, Any]], str]:
    """
    Perform an advanced web search using the Tavily API to find real-time information, 
    news, or travel itineraries.
    
    Use this tool when you need to find:
    - Current events or news (set topic="news")
    - Travel itineraries, guides, and blogs
    - Facts that are not in your internal knowledge base
    
    Args:
        query (str): The search query. Be specific (e.g., "3 day itinerary for Tokyo" instead of "Tokyo").
        country (str): should be country name: for example china, united states etc
        max_results (int): The maximum number of search results to return. Defaults to 5.
        search_depth (str): "basic" for fast results, "advanced" for high-quality content. Defaults to "advanced".
        topic (str): "general" for most queries, "news" for recent events. Defaults to "general".

    Returns:
        list[dict]: A list of dictionaries containing 'url', 'content', and 'title' for each result.
    """
    return web_search_service.execute(query, country, max_results, search_depth, topic)