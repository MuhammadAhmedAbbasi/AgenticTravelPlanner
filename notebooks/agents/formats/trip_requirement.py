from pydantic import BaseModel, Field
from typing import List

class TripRequirement(BaseModel):
    Departure: str = None
    Destination: List['str'] = None
    StartDate: str = None
    Duration: str = None
    Budget: str = None
    Interest: List[str] = None
    AllDetails: bool = False
    ExtraDetail: List[str] = None

    def is_complete(self) -> bool:
        return all([self.Destination, self.StartDate, self.Duration, self.Budget, self.Interest, self.AllDetails, self.ExtraDetail])


class ConversationFormat(BaseModel):
    Departure: str = None
    Destination: List['str'] = Field(None, description = "The place you want to go")
    StartDate: str = Field(None, description = "The date to start the trip: YYYY-MM-DD")
    Duration: str = Field(None, description = "The total number of days planned for trip")
    Budget: str = Field(None, description = "The overall budget of the trip")
    Interest: List[str] = Field(None, description = "The personality of person, Reccomendations are givenm based on the Interest of person")
    AllDetails: bool = Field(False, description = "True, if all details are completed, otherwise False")
    ExtraDetail: List[str] = Field(None, description = "Some Extra Information to provide")
    Response: str = Field(None, description = "The response of Model")

