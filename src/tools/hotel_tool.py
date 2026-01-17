from langchain.tools import tool
from serpapi import GoogleSearch
from src.config.settings import settings
from src.logging.logging import setup_logger

logger = setup_logger(__file__)

class HotelFindingTool:
    def __init__(self):
        self.serapi = settings.serpapi_key

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
            res = search.get_dict()
            print(f"The raw result is: {res}") 
            results = self._parse_data(res, place_name)
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