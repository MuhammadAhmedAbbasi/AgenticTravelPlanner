# Libraries
from langchain.tools import tool
from serpapi import GoogleSearch
from src.config.settings import settings
from src.logging.logging import setup_logger

logger = setup_logger(__file__)


class AttractionFindingTool:
    def __init__(self):
        self.serapi = settings.serpapi_key
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
            res = search.get_dict()
            print(f"Raw Result: {res}")
            results = self._parse_data(res, place_name)
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