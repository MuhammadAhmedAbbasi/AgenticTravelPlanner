# Libraries
import googlemaps
import uuid
import os
import sys

project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
    
from langchain.agents import create_agent, AgentState
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Literal, Optional, Dict
from tavily import TavilyClient
from pydantic import BaseModel, Field
from datetime import datetime
from langgraph.graph import StateGraph, START, END

from typing import Any
from langchain.agents.middleware import before_model, ModelRequest
from langchain.messages import SystemMessage

# API and environments
os.environ["GPLACES_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
tavily_api = os.environ["TAVILY_API_KEY"]
api =os.environ["GPLACES_API_KEY"]
gmaps = googlemaps.Client(api)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
parent_model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0, max_retries = 3, timeout=160)
tavily_client = TavilyClient(tavily_api)
checkpointer = InMemorySaver()


def clean_text(text_data, max_chars=150):
    """
    1. Extracts text if input is a dict (for highlighted_review).
    2. Truncates text to max_chars.
    3. Ensures no words are cut in half.
    """
    # Handle case where review is a dictionary {'text': '...', ...}
    if isinstance(text_data, dict):
        text = text_data.get('text', '')
    else:
        text = str(text_data) if text_data else ""

    # Return default if empty
    if not text:
        return "No details available."

    # If it's short enough, return it
    if len(text) <= max_chars:
        return text

    # Truncate and add ellipsis, trying to cut at a space
    truncated = text[:max_chars]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0] # Cut at last space
    
    return truncated + "..."

@tool
def attraction_finding_tool(place_name: str) -> list[dict]:
    """  
    Find popular attractions in a city or country.

    Args:
        place_name (str): Name of the city or country.

    Returns:
        list[dict]: List of up to 5 attractions with details:
            - title (str)
            - description (str)
            - rating (str/float)
            - highlighted_review (str)
        If no attractions found, returns a list with a dict containing an "error" key.
    """
    print("Starting Attraction Finding Details....")
    params = {
    "engine": "tripadvisor",
    "q": place_name,
    "ssrc": "A",
    "api_key": ""
    }

    search = GoogleSearch(params)
    try:

        results = search.get_dict()
        attraction_places = results.get("places", [])
    except Exception as e:
        return [{"error": f"There are no attraction places found in {place_name}."}]
    if not attraction_places:
        return []

    attraction_details = []

    for num in range(5):
        attraction = attraction_places[num]
        
        attraction_details.append(
            {
                "title": attraction.get('title', []),
                "description": clean_text(attraction.get('description', []),max_chars = 150),
                "rating": attraction.get('rating', []),
                "highlighted_review": clean_text(attraction.get('highlighted_review', []),max_chars = 150)
            }
        )
    print(f"Attraction Details Fetched: {attraction_details}")
    return attraction_details
    
@tool
def restaurant_finding_tool(place_name: str) -> list[dict]:
    """
    Tool Name: Restaurant Finder

    Purpose:
        Find top restaurants in a specified city using TripAdvisor.

    Input:
        place_name (str): Name of the city or country.

    Output:
        List of dictionaries (up to 5 items), each containing:
            - title (str): Name of the restaurant
            - description (str): Short description
            - rating (str/float): Average user rating
            - highlighted_review (str): Notable user review
        If no restaurants are found, returns a list with a dictionary containing an "error" key.

    Usage Instructions for AI:
        Use this tool when a user asks about restaurants or places to eat in a specific city.
    """
    print("Starting Restaurant Finding Tool...")
    params = {
        "engine": "tripadvisor",
        "q": place_name,
        "ssrc": "r",  # 'r' for restaurants
        "api_key": ""
    }

    search = GoogleSearch(params)

    try:
        results = search.get_dict()
        places = results.get("places", [])
    except Exception as e:
        return [{"error": f"Error fetching restaurants: {e}"}]

    if not places:
        return [{"error": f"No restaurants found in {place_name}."}]

    top_places = places[:5]

    restaurant_details = []
    for place in top_places:
        restaurant_details.append({
            "title": place.get("title", ""),
            "description": clean_text(place.get('description', []),max_chars = 150),
            "rating": place.get("rating", ""),
            "highlighted_review":clean_text(place.get('highlighted_review', []),max_chars = 150),
        })
    print(f"Restaurant Details Fetched: {restaurant_details}")
    return restaurant_details
    
import os
from serpapi import GoogleSearch

@tool
def hotel_finding_tool(place_name: str) -> list[dict]:
    """
    Tool Name: Hotel Finder

    Purpose:
        Find top hotels in a specified city using TripAdvisor.

    Input:
        place_name (str): Name of the city or country.

    Output:
        List of dictionaries (up to 5 items), each containing:
            - title (str): Name of the hotel
            - description (str): Short description
            - rating (str/float): Average user rating
            - highlighted_review (str): Notable user review
        If no hotels are found, returns a list with a dictionary containing an "error" key.

    Usage Instructions for AI:
        Use this tool when a user asks about hotels, accommodations, or places to stay in a specific city.
    """
    print(f"Finding The Hotels using Hotel Finding Tools...")
    params = {
        "engine": "tripadvisor",
        "q": place_name,
        "ssrc": "h",  # 'h' for hotels
        "api_key": ""
    }

    search = GoogleSearch(params)

    try:
        results = search.get_dict()
        places = results.get("places", [])
    except Exception as e:
        return [{"error": f"Error fetching hotels: {e}"}]

    if not places:
        return [{"error": f"No hotels found in {place_name}."}]

    top_places = places[:5]

    hotel_details = []
    for place in top_places:
        hotel_details.append({
            "title": place.get("title", ""),
            "description": clean_text(place.get('description', []),max_chars = 150),
            "rating": place.get("rating", ""),
            "highlighted_review": clean_text(place.get('highlighted_review', []),max_chars = 150)
        })
    print(f"Hotel Details Fetched: {hotel_details}")
    
    return hotel_details

trip_advisor_prompt = """You are CityDiscoveryAdvisor. Find attractions, hotels, and restaurants for cities using TripAdvisor tools.

TOOLS:
- attraction_finding_tool(place_name): Top 5 attractions
- hotel_finding_tool(place_name): Top 5 hotels
- restaurant_finding_tool(place_name): Top 5 restaurants

USAGE:
- "things to do" → attractions
- "where to stay" → hotels
- "where to eat" → restaurants
- General city query → use all 3 tools

RULES:
1. Only use tool outputs, never fabricate data
2. If tool returns error, report: "No {category} found for {place}"
3. Present all results (up to 5 per category)

FORMAT:
**{Category} in {City}:**
1. {Name} ({Rating}) - {Description}
   "{Highlighted Review}"

**Note:** {Any errors or limitations}
"""


trip_advisor_agent = create_agent(model = model, system_prompt = trip_advisor_prompt, tools = [attraction_finding_tool, hotel_finding_tool, restaurant_finding_tool])

@tool
def trip_advisor_tool(request: str):
    """
    Delegates queries about city-specific recommendations (Attractions, Hotels, Restaurants) to the Trip Advisor Specialist.

    Use this tool when the user asks for:
    - "Things to do", "Tourist attractions", "Places to visit", "Sightseeing".
    - "Where to stay", "Hotels", "Accommodation", "Resorts".
    - "Where to eat", "Restaurants", "Food spots", "Best cafes".
    - Comprehensive city guides (e.g., "Plan a day in London").

    Args:
        request (str): The full natural language query (e.g., "Recommend top hotels and food in Paris").

    Do NOT use this tool for:
    - Flights (use flight tools).
    - Distance or travel logistics (use distance tools).
    """
    result = trip_advisor_agent.invoke({"messages": [{"role": "user", "content": request}]})
    return result["messages"][-1].content[0]['text']