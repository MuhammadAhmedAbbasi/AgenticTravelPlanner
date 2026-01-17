# Libraries

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools.flight_search_tool import One_way_flight_search

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
checkpointer = InMemorySaver()

class FlightSpecialistAgent:
    def __init__(self, model, flight_tool):

        prompt = self.prompt_initialize()
        self.agent = self.agent_intialize(model, flight_tool, prompt)

    def prompt_initialize(self) -> str:
        # 4. Define System Prompt
        return """You are the FlightLogisticsSpecialist. Your sole purpose is to find one-way flight options using the One_way_flight_search tool.

        TOOLS:
        - One_way_flight_search(departure_id, arrival_id, travel_date): Searches for flights.
        Thinking and Action:
            - iF THERE ARE MULTIPLE CITIES IN DESTINATION, THEN YOU HAVE TO FIND THE FLIGHTS FROM DEPARTURE TO ALL DESTINATION AND THEN ALL COMBINATIONS BETWEEN DESTINATIONS AS WELL.
                EXAMPLE: Departure Taiyuan, Destination: [Islamabad, Karachi]. -> TAIYUAN -> iSLAMABAD, Taiyuan -> Karachi, Islamabad -> Karachi, -> Karachi-> Islamabad.
                Finally make a report where tell all options.

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
        - If the tool returns "Failed to Fetch" or "No Flights", first try with other names and still didn't find then tell the user.
        - If user provides country names instead of the city name, then for tool use assume the capital of those countries and then search for flight details
        
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