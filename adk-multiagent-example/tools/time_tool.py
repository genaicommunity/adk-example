"""Time tool for getting current time in different cities."""

from datetime import datetime
from typing import Dict


def get_current_time(city: str) -> Dict[str, str]:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city to get the time for.

    Returns:
        A dictionary containing the status, city name, and current time.
    """
    current_time = datetime.now().strftime("%I:%M %p")
    return {
        "status": "success",
        "city": city,
        "time": current_time,
        "message": f"The current time in {city} is {current_time}"
    }
