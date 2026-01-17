from langchain.tools import tool
from serpapi import GoogleSearch

# Libraries
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import settings

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
checkpointer = InMemorySaver()
class HotelFindingTool:
    def __init__(self):
        self.serapi = settings

    def execute(self, place_name):
        return self._extract_places(place_name)

    def _extract_places(self, place_name):
        try:
            params = {
                "engine": "tripadvisor",
                "q": place_name,
                "ssrc": "h",  # 'h' specifically targeting Hotels
                "api_key": self.serapi
            }
            search = GoogleSearch(params)
            results = self._parse_data(search.get_dict(), place_name)
            return results
        except Exception as e:
            return {
                "status": "Error",
                "place_name": place_name,
                "hotel_details": [],
                "Error": str(e)
            }

    def _parse_data(self, results, place_name):
        hotel_details = []
        places = results.get("places", [])
        
        if not places:
            return {
                "status": "Failed",
                "place_name": place_name,
                "hotel_details": hotel_details,
                "result": "No Hotels Found"
            }

        # Limit to top 5
        limit = min(5, len(places))
        for num in range(limit):
            place = places[num]
            hotel_details.append(
                {
                    "title": place.get('title', 'Unknown'),
                    "description": self.clean_text(place.get('description', []), max_chars=150),
                    "rating": place.get('rating', 'N/A'),
                    "highlighted_review": self.clean_text(place.get('highlighted_review', []), max_chars=150)
                }
            )
            
        return {
            "status": "Success",
            "place_name": place_name,
            "hotel_details": hotel_details,
            "result": "Hotels Found"
        }

    def clean_text(self, text_data, max_chars=150):
        if isinstance(text_data, dict):
            text = text_data.get('text', '')
        else:
            text = str(text_data) if text_data else ""

        if not text:
            return "No details available."

        if len(text) <= max_chars:
            return text

        truncated = text[:max_chars]
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        
        return truncated + "..."

# Initialize Service
hotel_service = HotelFindingTool()

@tool
def hotel_finding_tool(place_name: str) -> dict:
    """ 
    Find top hotels and accommodations in a specific city.

    Args:
        place_name (str): Name of the city.

    Returns:
        Dict: Contains keys: status, place_name, hotel_details (list), result.
        
        hotel_details contains:
            - title
            - description
            - rating
            - highlighted_review
    """
    return hotel_service.execute(place_name)


class RestaurantFindingTool:
    def __init__(self):
        self.serapi = settings

    def execute(self, place_name):
        return self._extract_places(place_name)

    def _extract_places(self, place_name):
        try:
            params = {
                "engine": "tripadvisor",
                "q": place_name,
                "ssrc": "r",  # 'r' specifically targeting Restaurants
                "api_key": self.serapi
            }
            search = GoogleSearch(params)
            results = self._parse_data(search.get_dict(), place_name)
            return results
        except Exception as e:
            return {
                "status": "Error",
                "place_name": place_name,
                "restaurant_details": [],
                "Error": str(e)
            }

    def _parse_data(self, results, place_name):
        restaurant_details = []
        places = results.get("places", [])
        
        if not places:
            return {
                "status": "Failed",
                "place_name": place_name,
                "restaurant_details": restaurant_details,
                "result": "No Restaurants Found"
            }

        # Limit to top 5
        limit = min(5, len(places))
        for num in range(limit):
            place = places[num]
            restaurant_details.append(
                {
                    "title": place.get('title', 'Unknown'),
                    "description": self.clean_text(place.get('description', []), max_chars=150),
                    "rating": place.get('rating', 'N/A'),
                    "highlighted_review": self.clean_text(place.get('highlighted_review', []), max_chars=150)
                }
            )
            
        return {
            "status": "Success",
            "place_name": place_name,
            "restaurant_details": restaurant_details,
            "result": "Restaurants Found"
        }

    def clean_text(self, text_data, max_chars=150):
        if isinstance(text_data, dict):
            text = text_data.get('text', '')
        else:
            text = str(text_data) if text_data else ""

        if not text:
            return "No details available."

        if len(text) <= max_chars:
            return text

        truncated = text[:max_chars]
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        
        return truncated + "..."

# Initialize Service
restaurant_service = RestaurantFindingTool()

@tool
def restaurant_finding_tool(place_name: str) -> dict:
    """ 
    Find top restaurants in a specific city.

    Args:
        place_name (str): Name of the city.

    Returns:
        Dict: Contains keys: status, place_name, restaurant_details (list), result.
        
        restaurant_details contains:
            - title
            - description
            - rating
            - highlighted_review
    """
    return restaurant_service.execute(place_name)




class AttractionFindingTool:
    def __init__(self):
        self.serapi = settings
    def execute(self, place_name):
        return self._extract_places(place_name)
    def _extract_places(self, place_name):
        
        try:
            params = {
                "engine": "tripadvisor",
                "q": place_name,
                "ssrc": "A",
                "api_key": self.serapi
                }
            search = GoogleSearch(params)
            results = self._parse_data(search.get_dict(), place_name)
            return results
        except Exception as e:
            return {
                "status": "Error",
                "place_name": place_name,
                "attraction_details": [],
                "Error": str(e)
            }
    def _parse_data(self, results, place_name):
        attraction_details = []
        attraction_places = results.get("places", [])
        if not attraction_places:
            return {
                "status": "Failed",
                "place_name":place_name,
                "attraction_details": attraction_details,
                "result": "No Attraction Places Found"
            }
        for num in range(5):
            attraction = attraction_places[num]
            
            attraction_details.append(
                {
                    "title": attraction.get('title', []),
                    "description": self.clean_text(attraction.get('description', []),max_chars = 150),
                    "rating": attraction.get('rating', []),
                    "highlighted_review": self.clean_text(attraction.get('highlighted_review', []),max_chars = 150)
                }
            )
        return {
            "status": "Success",
            "place_name": place_name,
            "attraction_details": attraction_details,
            "result": "Attraction Places Found"
        }
    def clean_text(self, text_data, max_chars=150):
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

    
attraction_service = AttractionFindingTool()

@tool
def attraction_finding_tool(place_name: str) -> list[dict]:
    """  
    Find popular attractions in a city or country.

    Args:
        place_name (str): Name of the city or country.

    Returns:
        Dict: Dict contain: Status: str, place_name: str, attraction_details: List, result: str
        
        attraction_details: List of up to 5 attractions with details:
            - title (str)
            - description (str)
            - rating (str/float)
            - highlighted_review (str)
    """

    return attraction_service.execute(place_name)




tools = [attraction_finding_tool, hotel_finding_tool, restaurant_finding_tool]

class DestinationInfoAgent:
    def __init__(self, model, tools):

        prompt = self.prompt_initialize()
        self.agent = self.agent_intialize(model, tools, prompt)

    def prompt_initialize(self) -> str:
        # 4. Define System Prompt
        return """You are CityDiscoveryAdvisor. Find attractions, hotels, and restaurants for cities using TripAdvisor tools.

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
    def agent_intialize(self, model, tools, prompt):
        # 5. Create the Agent Graph
        return create_agent(
            model=model, 
            tools=tools, 
            system_prompt=prompt
            )

    def invoke(self, user_input: str):
        """
        Run the agent with a user query.
        Args:
            user_input (str): The user's prompt (e.g., "Flights from LHE to JFK").
            thread_id (str): Unique ID for conversation memory.
        """
        res = self.agent.invoke(user_input)
        
        # Return the last message (the AI's response)
        return res

# Initialize the instance for import elsewhere
destination_agent_service = DestinationInfoAgent(model, tools)