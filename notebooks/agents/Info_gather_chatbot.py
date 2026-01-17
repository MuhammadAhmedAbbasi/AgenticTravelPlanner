import os
    
from langchain.agents import create_agent
from langchain.tools import tool
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


# API and environments
os.environ["GPLACES_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"


class TimeTool:
    def execute(self):
        return self._get_current_time()

    def _get_current_time(self):
        try:
            now = datetime.now()
            
            # Format parts
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            weekday = now.strftime("%A") # e.g., "Friday"

            return {
                "status": "Success",
                "date": date_str,
                "time": time_str,
                "day_of_week": weekday,
                "result": f"Today is {weekday}, {date_str}. The current time is {time_str}."
            }
        except Exception as e:
            return {
                "status": "Error",
                "result": f"Failed to fetch time: {str(e)}"
            }

# Initialize Service
time_service = TimeTool()


class ConversationFormat(BaseModel):
    Departure: str = None
    Destination: List['str'] = Field(None, description = "The place you want to go")
    StartDate: str = Field(None, description = "The date to start the trip: YYYY-MM-DD")
    Duration: str = Field(None, description = "The total number of days planned for trip")
    Budget: str = Field(None, description = "The overall budget of the trip")
    Interest: List[str] = Field(None, description = "The personality of person, Reccomendations are givenm based on the Interest of person")
    ExtraDetail: List[str] = Field(None, description = "Some Extra Information to provide")
    Response: str = Field(None, description = "The response of Model")


@tool
def time_tool() -> dict:
    """
    Get the current date, time, and day of the week.
    
    Returns:
        Dict: Contains keys: status, date, time, day_of_week, result.
    """
    return time_service.execute()


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
                """
        return conversation_system_prompt
    def ask(self, question: str, missing_list) -> str:
        modified_input = f" User Input: {question},  Remaining Information: {missing_list} "
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