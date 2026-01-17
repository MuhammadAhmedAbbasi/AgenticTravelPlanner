# Initializing the Base Class to ensure correct formatting of model
# Libraries
import googlemaps
import os
    
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal
from pydantic import BaseModel, Field



# API and environment
gmaps = googlemaps.Client(api)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
parent_model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0, max_retries = 3, timeout=160)


class DistanceToolFormatting(BaseModel):
    origins: str = Field(description = "The starting point from where we want to see")
    destinations: str = Field(description = "The Ending Point which is used to calculate the distance")
    mode: Literal["walking", "driving", "transit"] = Field(default = "walking", description = "The mode which is used to calculate the duration")

# Tool Calling for distance matrix calculation
@tool("distance_matrix", description = "This tool is used to measure the distance between two locations", args_schema = DistanceToolFormatting)
def distance_measurement_tool(origins: str, destinations: str, mode: str = "walking"):
    """ This function is used to measure the distance between two locations. 
        The locations should be in str and the origins is the location person want to go from and destinations is the location person want to go to
        The mode is the mode of travel, it can be "walking", "driving" or "transit" 
        The return or outputs of this tools is string which contain the distance and time taken. 
    """
    print("Starting Distance Measurement Tool...")
    result = gmaps.distance_matrix(origins, destinations, mode = mode)
    print(f"The result from distance tool: {result}")
    distances = []
    durations = []

    for element in result['rows']:
        for status in element['elements']:
            if status['status'] == "ZERO_RESULTS":
                return (
                    "No ground route found between the selected locations. "
                    "This route may cross restricted borders or require air travel."
                )
    for row in result['rows']:
        for sub_row in row["elements"]:
            distance = sub_row['distance']['text']
            duration = sub_row['duration']['text']
            distances.append(distance)
            durations.append(duration)
    final_formatted_result = f"The duration between {origins} and {destinations} is {durations} min and distance is {distances} km"
    print(f"Distance is found from {origins} to {destinations} which is {final_formatted_result}")
    return final_formatted_result



distance_prompt = """You are DistanceToolAgent. Your job is to calculate the distance and estimated time between two locations using the distance_matrix tool.

TOOLS:
- distance_measurement_tool(origins, destinations, mode): Returns the distance and time between two locations.

USAGE:
- "from [origin] to [destination]" → calculate distance and time for the specified route
- "distance between [origin] and [destination] by [mode]" → calculate distance and time with a specified mode of travel ("walking" or "driving")

RULES:
1. Only use tool outputs, never fabricate data.
2. If tool returns an error such as "ZERO_RESULTS", report: "No ground route found between the selected locations. This route may cross restricted borders or require air travel."
3. Present the results in the following format:
   - "The duration between [origin] and [destination] is [duration] and distance is [distance]."
4. Handle both the distance and duration results appropriately. If multiple results exist, present them all.

FORMAT:
The result should be in the format:
"The [mode] duration between [origins] and [destinations] is [duration] and distance is [distance]."

EXAMPLES:
- "What is the distance and time from New York to Los Angeles by driving?"
- "How long does it take to walk from Paris to Berlin?"

RULES FOR SPECIAL CASES:
- If there are multiple results, return the best match.
- If the distance_matrix tool returns no valid results, respond with a message stating no route is found.
"""
distance_agent = create_agent(model = model, tools = [distance_measurement_tool], system_prompt = distance_prompt)
#distance_agent.invoke({"messages": "Tell me distance and time from lahore to islamabad, both walking, driving and transit"})

# @tool
# def distance_agent_tool(request: str):
#     """ 
#     Delegates distance and travel duration queries to the specialized Distance Agent.
    
#     Use this tool when the user asks for:
#     - Physical distance between two locations (cities, landmarks, addresses).
#     - Estimated travel time (duration) for driving, walking, or transit.
#     - Comparisons of travel modes (e.g., "is it faster to walk or drive?").

#     Args:
#         request (str): The full natural language query regarding distance or travel time 
#                        (e.g., "How long does it take to drive from NYC to Boston?").
    
#     Do NOT use this tool for:
#     - Flight durations (use flight tools).
#     - Generic location information or history.
#     """
#     # Invoking the sub-agent
#     result = distance_agent.invoke({"messages": [{"role": "user", "content": request}]})
    
#     # Note: Ensure you access the content correctly based on your LangChain version
#     # usually result["messages"][-1].content
#     return result["messages"][-1].content
