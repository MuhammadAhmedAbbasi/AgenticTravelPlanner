import os
   
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from typing import List
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.database.local_database import StoreMemory
from src.utils.helping_class.trip_requirements import TripRequirement
from src.tools.time_gather_tool import time_tool
from src.utils.helping_class.conversation_format import ConversationFormat

# API and environments
os.environ["GPLACES_API_KEY"] = settings.google_places_key
os.environ["GOOGLE_API_KEY"] = settings.google_api_key
os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
os.environ["http_proxy"] = settings.http_proxy
os.environ["https_proxy"] = settings.https_proxy

checkpointer = InMemorySaver()
local_database = StoreMemory()

class ConversationFormat(BaseModel):
    Departure: str = None
    Destination: List['str'] = Field(None, description = "The place you want to go")
    StartDate: str = Field(None, description = "The date to start the trip: YYYY-MM-DD")
    Duration: str = Field(None, description = "The total number of days planned for trip")
    Budget: str = Field(None, description = "The overall budget of the trip")
    Interest: List[str] = Field(None, description = "The personality of person, Reccomendations are givenm based on the Interest of person")
    ExtraDetail: List[str] = Field(None, description = "Some Extra Information to provide")
    Response: str = Field(None, description = "The response of Model")

class InformationGatherChatbot():
    def __init__(self, model, response_formatting, tools):
        
        conversation_prompt = self.prompt()
        self.agent = self.initialize_agent(model, conversation_prompt, response_formatting, tools)

    def initialize_agent(self, model, prompt, response_format, tools):
        chatbot = create_agent(model = model, system_prompt = prompt, response_format = response_format, tools = tools)
        return chatbot
    def prompt(self):
        conversation_system_prompt = """
        You are a friendly Travel Planning Assistant. Your role is to gather information from the user.
         
            Tools Available:
                1. time_tool: This tool is used when user don't give you time and ask you to find yourself

            CONVERSATION RULES:
                1. Analyze the 'User Input' which is users original response
                2. Extract ANY new information provided for: Departure, Destination, StartDate, Duration, Budget, Interest, ExtraDetail.
                3. If the user DOES NOT mention a specific field in THIS message, return None for that field. DO NOT make up data.
                4. Generate a friendly 'Response' asking for the items in 'missing_list'.
                5. "Remaining Information" which shows the things left to be filled
            Important Point:
                - If someone give the destination as country instead of city, ask him to tell the city and also suggest him few famous cities to select and if he didn't select, select any three cities and add them as list of destination.
                """
        return conversation_system_prompt
    def ask(self, question: str, missing_list) -> str:

        modified_input = f" User Input: {question},  Remaining Information: {missing_list} "
        print(modified_input)
        response = self.agent.invoke({"messages":[{"role": "user", "content": modified_input}]})
        return {
            "Departure": response.get("structured_response").Departure,
            "Destination": response.get("structured_response").Destination,
            "StartDate": response.get("structured_response").StartDate,
            "Duration": response.get("structured_response").Duration,
            "Budget": response.get("structured_response").Budget,
            "Interest": response.get("structured_response").Interest,
            "Response": response.get("structured_response").Response,
            "ExtraDetail": response.get("structured_response").ExtraDetail
        }