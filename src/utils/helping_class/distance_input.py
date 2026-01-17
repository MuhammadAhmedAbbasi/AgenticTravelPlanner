from pydantic import BaseModel, Field


class DistanceInput(BaseModel):
    origins: str = Field(..., description="The starting location (e.g., 'New York, NY').")
    destinations: str = Field(..., description="The destination location (e.g., 'Boston, MA').")
    mode: str = Field("walking", description="Mode of travel: 'walking', 'driving', 'bicycling', or 'transit'.")