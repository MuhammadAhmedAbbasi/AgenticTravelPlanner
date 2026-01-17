# Libraries
from ast import Dict
import os

from langchain.tools import tool
from serpapi import GoogleSearch
from src.config.settings import settings
from src.utils.validators import flight_code_check, date_check
from src.logging.logging import setup_logger

logger = setup_logger(__file__)
os.environ["http_proxy"] = settings.http_proxy
os.environ["https_proxy"] = settings.https_proxy



class FlightSearchTool:
    def __init__(self, setting = settings):
        self.serpapi = settings.serpapi_key
    def execute(self, departure_id: str, arrival_id: str, travel_date: str):
        """ 
        This function is reponsible for final execution of code
        """
        if not flight_code_check(departure_id):
            raise ValueError(f"The departure id: {departure_id} is wrong")
        if not flight_code_check(arrival_id):
            raise ValueError(f"The departure id: {arrival_id} is wrong")
        if not date_check(travel_date):
            raise ValueError(f"The Date Information is incorrect: {travel_date}")

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
