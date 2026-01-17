# Libraries
import os
import sys

project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
    
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal
from tavily import TavilyClient


# API and environments
os.environ["GPLACES_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = "-"
os.environ["TAVILY_API_KEY"] = ""
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
tavily_api = os.environ["TAVILY_API_KEY"]
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
tavily_client = TavilyClient(tavily_api)

@tool("Web_Search_Tool", description = " This tool is used when there is a need to search online.")
def web_search_tool(
    query: str, 
    country: str = "us", 
    max_results: int = 5,
    search_depth: Literal["basic", "advanced"] = "advanced",
    topic: Literal["general", "news"] = "general"
):
    """
    Perform an advanced web search using the Tavily API to find real-time information, 
    news, or travel itineraries.
    
    Use this tool when you need to find:
    - Current events or news (set topic="news")
    - Travel itineraries, guides, and blogs
    - Facts that are not in your internal knowledge base
    
    Args:
        query (str): The search query. Be specific (e.g., "3 day itinerary for Tokyo" instead of "Tokyo").
        country (str): The 2-letter ISO country code to bias results towards (e.g., "us", "fr", "jp"). Defaults to "us".
        max_results (int): The maximum number of search results to return. Defaults to 5.
        search_depth (str): "basic" for fast results, "advanced" for high-quality content. Defaults to "advanced".
        topic (str): "general" for most queries, "news" for recent events. Defaults to "general".

    Returns:
        list[dict]: A list of dictionaries containing 'url', 'content', and 'title' for each result.
    """
        
    try:
        if topic == "general":
            response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                topic=topic,
                country=country,
                max_results=max_results
            )
        else:
            response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                topic=topic,
                max_results=max_results
            )
        return response.get("results", [])

    except Exception as e:
        return f"Error performing search: {str(e)}"

web_search_system_prompt = """WebSearchAgent: Search the web for real-time information.

TOOL: web_search_tool(query, max_results, search_depth, topic)

PARAMETERS:
- query: Specific search query
- max_results: 3-5 recommended
- search_depth: Always "advanced"
- topic: "news" for this week's events, "general" for everything else

SEARCH STRATEGY:
1. For policies, visa rules, or guides: START with topic="general"
2. For breaking news or events: Use topic="news"
3. If results are irrelevant, try rephrasing the query or switching topic

EXAMPLES:
- "Pakistan visa policy" → topic="general" (policy info, not breaking news)
- "Pakistan earthquake today" → topic="news" (current event)
- "Tokyo 3-day itinerary" → topic="general" (travel guide)

OUTPUT:
**Search Results: {query}**

1. [{Title}]({URL}) - {Key info}
2. [{Title}]({URL}) - {Key info}

**Summary:** {Brief synthesis}

If results don't match the query, try a different search or report no relevant info found."""



# @tool
# def web_search_agent_tool(request: str):
#     """
#     Delegates general information, news, and itinerary search queries to the Web Search Specialist.

#     Use this tool when the user asks for:
#     - Real-time information or breaking news (e.g., "What happened in X today?").
#     - Travel itineraries, blogs, or guides (e.g., "3-day trip to Tokyo").
#     - Factual information not covered by other specific tools (e.g., "Visa requirements for X", "History of Y").

#     Args:
#         request (str): The full natural language query describing what information is needed.

#     Do NOT use this tool for:
#     - Specific distance calculations (use distance tools).
#     - Specific hotel/restaurant/attraction lists if a dedicated tool exists (unless general research is needed).
#     """
#     result = web_search_agent.invoke({"messages": [{"role": "user", "content": request}]})
#     return result["messages"][-1].content[0]['text']