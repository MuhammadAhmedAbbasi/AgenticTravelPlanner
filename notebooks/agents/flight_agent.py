# Libraries
import googlemaps
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from serpapi import GoogleSearch
from typing import Dict

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


class FlightSearchTool:
    def __init__(self):
        self.serpapi = ""
    def execute(self, departure_id: str, arrival_id: str, travel_date: str):
        """ 
        This function is reponsible for final execution of code
        """

        return self._flight_info_extract(departure_id, arrival_id, travel_date) 

    def _flight_info_extract(self, departure_id, arrival_id, travel_date):
        try:
            params = {
                        "engine": "google_flights",
                        "departure_id": departure_id,
                        "arrival_id": arrival_id,
                        "currency": "USD",
                        "type": "2",
                        "outbound_date": travel_date,
                        "api_key": self.serpapi
                    }
            search = GoogleSearch(params)
            results = self._parse_flight_details(search.get_dict(),departure_id, arrival_id, travel_date)
            return results
        except Exception as e:
            return {
                "status": "Error",
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "travel_date": travel_date,
                "error_message": str(e)

            }
    def _parse_flight_details(self, results: Dict, departure_id, arrival_id, travel_date):
        if results.get('error'):
            return {
                "status": "Error",
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "travel_date": travel_date,
                "error_message": results.get('error')
            }
        try:
            lowest_available_price = results['price_insights']['lowest_price']
            current_price_status = results['price_insights']['price_level']
            average_price_status= results['price_insights']['typical_price_range']
            departure_airport = results['airports'][0]['departure'][0]['airport']['name']
            arrival_airport = results['airports'][0]['arrival'][0]['airport']['name']
            best_flight_result, best_flight_remarks = self.flight_info_extract(results.get("best_flights", []), departure_airport, arrival_airport, travel_date)
            other_flight_result, other_flight_remarks = self.flight_info_extract(results.get("other_flights", []), departure_airport, arrival_airport, travel_date) 
            return {
                "status": "Success",
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "travel_date": travel_date,
                "lowest_available_price":lowest_available_price,
                "current_price_status": current_price_status,
                "average_price_status": average_price_status,
                "best_flight_result":{"best_flight_result":best_flight_result, "best_flight_remarks":best_flight_remarks},
                "other_flight_result":{"other_flight_result":other_flight_result, "other_flight_remarks":other_flight_remarks}}
        except Exception as e:
            return {
                "status":"Error",
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "travel_date": travel_date,
                "error_message": results.get('error')
            }
    def flight_info_extract(self, flight_option, departure_id: str, arrival_id: str, travel_date: str):
        all_options= []
        # other_flights = results['other_flights']
        if not flight_option:
            result = f"There are no Flights from: {departure_id} to {arrival_id} on date: {travel_date}"
            return all_options, result
        for idx, flight in enumerate(flight_option):
            price = flight.get("price", -1)
            if price >= 0:
                all_options.append(
                    {
                        "Flight Option": idx+1,
                        "price": price,
                        "Layover": [layover_name.get('name', "") for layover_name in flight.get('layovers', [])] if flight.get('layovers') else ["No Layover"],
                        "Total Flight Duration (hours)": round(flight.get('total_duration', 0)/60, 1)
                    }
                )
            else:
                continue
        all_options.sort(key = lambda x: x['price'])
        if not all_options:
            result = f"There is no Price available for all flights."
            return all_options, result 
        result = f"There are Flights from: {departure_id} to {arrival_id} on date: {travel_date}" 
        return all_options, result 

flight_tool = FlightSearchTool()

@tool
def One_way_flight_search(departure_id: str, arrival_id: str, travel_date: str):
    """
   Search for one-way flights between two airports on a specific date.
    Returns flight options with price, layovers, and duration details.
    
    Args:
        departure_id (str): Departure airport code (e.g., 'PEK' for Beijing)
        arrival_id (str): Arrival airport code (e.g., 'ISB' for Islamabad)
        travel_date (str): Travel date in YYYY-MM-DD format (e.g., '2026-03-03')
    
    Returns:
        Dict: Dictionary of Formatted flight search results with prices, durations, and layover information
    
    """
    return flight_tool.execute(departure_id, arrival_id, travel_date)




class FlightSpecialistAgent:
    def __init__(self, model, flight_tool):

        prompt = self.prompt_initialize()
        self.agent = self.agent_intialize(model, [flight_tool], prompt)

    def prompt_initialize(self) -> str:
        # 4. Define System Prompt
        return """You are the FlightLogisticsSpecialist. Your sole purpose is to find one-way flight options using the One_way_flight_search tool.

        TOOLS:
        - One_way_flight_search(departure_id, arrival_id, travel_date): Searches for flights.

        CRITICAL INPUT RULES:
        1. Airport Codes: The tool REQUIRES IATA airport codes (e.g., "LHE" for Lahore, "PEK" for Beijing, "JFK" for New York).
           - If the user provides a city name, YOU MUST convert it to the correct IATA code before calling the tool.
        2. Date Format: The tool REQUIRES dates in "YYYY-MM-DD" format.
           - If the user says "next Friday" or "March 3rd", convert it to "YYYY-MM-DD" relative to the current date.

        OUTPUT GUIDELINES:
        - Start with the "Lowest Available Price" and general price status.
        - Present "Best Flight Options" first (these offer the best balance of price/duration).
        - Summarize "Other Options" if they offer significantly cheaper prices but longer durations.
        - Highlight layovers explicitly.

        ERROR HANDLING:
        - If the tool returns "Failed to Fetch" or "No Flights", apologize and ask the user to verify the date or route.
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
flight_agent_service = FlightSpecialistAgent(model, One_way_flight_search)