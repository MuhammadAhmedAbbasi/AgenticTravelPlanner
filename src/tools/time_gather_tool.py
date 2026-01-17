from datetime import datetime
from langchain.tools import tool
from src.logging.logging import setup_logger

logger = setup_logger(__file__)

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

@tool
def time_tool() -> dict:
    """
    Get the current date, time, and day of the week.
    
    Returns:
        Dict: Contains keys: status, date, time, day_of_week, result.
    """
    return time_service.execute()