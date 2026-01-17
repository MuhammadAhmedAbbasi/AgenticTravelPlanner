from pydantic import BaseModel
from typing import List

class TripRequirement(BaseModel):
    Departure: str = None
    Destination: List['str'] = None
    StartDate: str = None
    Duration: str = None
    Budget: str = None
    Interest: List[str] = None
    ExtraDetail: List[str] = None

    def is_complete(self) -> bool:
        return all([self.Destination, self.StartDate, self.Duration, self.Budget, self.Interest, self.ExtraDetail])