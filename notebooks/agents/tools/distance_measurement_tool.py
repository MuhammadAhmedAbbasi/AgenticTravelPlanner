import googlemaps
from langchain.tools import tool
from pydantic import BaseModel, Field

# 1. Define the Input Schema (Good practice for structured tools)
class DistanceInput(BaseModel):
    origins: str = Field(..., description="The starting location (e.g., 'New York, NY').")
    destinations: str = Field(..., description="The destination location (e.g., 'Boston, MA').")
    mode: str = Field("walking", description="Mode of travel: 'walking', 'driving', 'bicycling', or 'transit'.")

# 2. Define the Class Service
class DistanceMatrixTool:
    def __init__(self):
        # Initialize the Google Maps client
        # Ensure 'GOOGLE_MAPS_API_KEY' is in your settings
        self.gmaps = googlemaps.Client(key=api)

    def execute(self, origins: str, destinations: str, mode: str):
        return self._calculate_distance(origins, destinations, mode)

    def _calculate_distance(self, origins, destinations, mode):
        try:
            # Call the Google Maps API
            result = self.gmaps.distance_matrix(origins, destinations, mode=mode)
            return self._parse_data(result, origins, destinations)
            
        except Exception as e:
            return {
                "status": "Error",
                "origin": origins,
                "destination": destinations,
                "distance_data": {},
                "result": f"Error calculating distance: {str(e)}"
            }

    def _parse_data(self, result, origins, destinations):
        # 1. Check for valid structure
        if not result.get('rows'):
            return self._format_failure(origins, destinations, "No data returned from API.")

        rows = result['rows'][0]
        elements = rows.get('elements', [])
        
        if not elements:
             return self._format_failure(origins, destinations, "No route elements found.")

        # 2. Check specific element status
        element = elements[0]
        status = element.get('status')

        if status == "ZERO_RESULTS":
            return self._format_failure(
                origins, 
                destinations, 
                "No ground route found. This may cross restricted borders or require air travel."
            )
        
        if status != "OK":
            return self._format_failure(origins, destinations, f"API Status: {status}")

        # 3. Extract successful data
        distance_text = element['distance']['text']
        duration_text = element['duration']['text']
        
        # 4. Construct Success Response
        return {
            "status": "Success",
            "origin": origins,
            "destination": destinations,
            "distance_data": {
                "distance": distance_text,
                "duration": duration_text,
                "mode": result.get("mode", "unknown") # sometimes api doesn't return mode explicitly in body
            },
            "result": f"The duration between {origins} and {destinations} is {duration_text} and distance is {distance_text}."
        }

    def _format_failure(self, origins, destinations, reason):
        return {
            "status": "Failed",
            "origin": origins,
            "destination": destinations,
            "distance_data": {},
            "result": reason
        }

# Initialize the Service
distance_service = DistanceMatrixTool()

# 3. Define the LangChain Tool
@tool("distance_matrix", args_schema=DistanceInput)
def distance_measurement_tool(origins: str, destinations: str, mode: str = "walking") -> dict:
    """ 
    Measure the distance and travel time between two locations.
    
    Returns:
        Dict: Contains keys: status, origin, destination, distance_data (dict), result.
    """
    return distance_service.execute(origins, destinations, mode)