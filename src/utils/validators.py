import re
from datetime import datetime

def flight_code_check(input: str):
    "This validator is used to check the flight code"
    pattern = r'^[A-Z]{3}$'
    if not re.match(pattern, input.upper()):
        return False
    return True

def date_check(date: str):
    pattern = r'\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date):
        return False
    date_stripped = datetime.strptime(date, "%Y-%m-%d")
    if date_stripped.year < datetime.now().year:
        return False
    if date_stripped.month < datetime.now().month:
        return False
    if date_stripped.date() < datetime.now().date():
        return False
    return True