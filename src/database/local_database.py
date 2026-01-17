import uuid

from datetime import datetime
from typing import List
from src.utils.helping_class.user_details import UserDetails


class StoreMemory():
    def __init__(self):
        self.users = {}
        self.trip_plans = {}
    def add_or_get_user(self, user_id: str = None, user_name = None, preferences = None, email: str = None):
        if preferences is None:
            preferences = {}
        if  user_id in self.users:
            return self.users[user_id]
        else:
            now = datetime.now().isoformat()
            user_details = UserDetails(
                UserName = user_name,
                UserID = user_id,
                DateCreated = now,
                Preferences = preferences,
                Email = email
            )
            self.users[user_id] = user_details
            return user_details

    def add_travel_details(self, user_id, Departure: str, Destination: List[str], StartDate: str, Duration: str, Budget: str, Interest: List[str], ExtraDetail: List[str]):
        trip_id = str(uuid.uuid4())
        trip_id = str(Destination) + trip_id
        trip_info = {
            "user_id": user_id,
            "trip_id": trip_id,
            "Departure": Departure,
            "Destination":Destination,
            "StartDate": StartDate,
            "Duration": Duration, 
            "Budget": Budget,
            "Interest": Interest,
            "ExtraDetail": ExtraDetail
        }
        self.trip_plans[trip_id] = trip_info

    def get_trip_details(self, user_id, specific_trip = False):
        if specific_trip == False:
            trip_details = [trips  for trips in self.trip_plans.values() if trips["user_id"] == user_id]
            return trip_details