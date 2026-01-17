from typing import List
from pydantic import Field
from langchain.agents import AgentState

class CustomState(AgentState):
    Departure: str = None
    Destination: List['str'] = Field(None, description = "The place you want to go")
    StartDate: str = Field(None, description = "The date to start the trip: YYYY-MM-DD")
    Duration: str = Field(None, description = "The total number of days planned for trip")
    Budget: str = Field(None, description = "The overall budget of the trip")
    Interest: List[str] = Field(None, description = "The personality of person, Reccomendations are givenm based on the Interest of person")
    AllDetails: bool = Field(False, description = "True, if all details are completed, otherwise False")
    ExtraDetail: List[str] = Field(None, description = "Some Extra Information to provide")
    Response: str = Field(None, description = "The response of Model")
    move_to_info_chatbot: bool = Field(False, description = "")
    previous_plan: str = None
    TravelMode: str = Field("Travel_Plan", description = "When you want plan from scratch, it is Travel_Plan and for Revision_Plan")
    flight_info: str = None
    hotel_info: str = None