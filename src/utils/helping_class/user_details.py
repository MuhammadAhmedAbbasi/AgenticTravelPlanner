from ast import Dict
from pydantic import BaseModel
from typing import Optional, Dict

class UserDetails(BaseModel):
    UserName: Optional[str]
    UserID: str
    DateCreated: Optional[str]
    Preferences: Dict
    Email: Optional[str]