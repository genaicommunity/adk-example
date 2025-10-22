"""Weather tool for getting weather information."""

import random
from typing import Dict


def get_weather(city: str) -> Dict[str, str]:
    """Returns mock weather information for a specified city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        A dictionary containing weather information.
    """
    # Mock weather data - in production, this would call a real weather API
    weather_conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    condition = random.choice(weather_conditions)
    temperature = random.randint(15, 30)

    return {
        "status": "success",
        "city": city,
        "condition": condition,
        "temperature": f"{temperature}°C",
        "message": f"The weather in {city} is {condition} with a temperature of {temperature}°C"
    }
