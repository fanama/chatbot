import requests
from bs4 import BeautifulSoup


from datetime import datetime
import pytz


import re


def parse_input(input_str: str):
    """
    Parse a math expression string into operands and operation.

    Supported formats:
        - Binary: "8 + 2", "5 * 3", "10 / 2"
        - Unary: "sqrt 16"
        - Percentage: "50 percent of 200"

    Returns:
        tuple: (a: float, b: float, operation: str)
    """
    input_str = input_str.lower().strip()

    # Match addition, subtraction, multiplication, division, power
    match = re.match(
        r"(-?\d+(\.\d+)?)\s*([\+\-\*/\^])\s*(-?\d+(\.\d+)?)", input_str)
    if match:
        a = float(match.group(1))
        op_symbol = match.group(3)
        b = float(match.group(4))
        op_map = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '^': 'pow'}
        return a, b, op_map[op_symbol]

    # Match square root
    match = re.match(r"(sqrt)\s*(-?\d+(\.\d+)?)", input_str)
    if match:
        a = float(match.group(2))
        return a, 0, "sqrt"

    # Match percentage: "x percent of y"
    match = re.match(
        r"(\d+(\.\d+)?)\s*percent\s*of\s*(\d+(\.\d+)?)", input_str)
    if match:
        a = float(match.group(1))
        b = float(match.group(3))
        return a, b, "percent"

    raise ValueError(f"Could not parse input: '{input_str}'")


def get_time(city: str) -> str:
    """
    Get the current local time for a given city.

    Args:
        city (str): Name of the city (e.g., "London", "New York").

    Returns:
        str: Current time in that city.
    """
    print("[TOOL] TIME invoked")

    city_timezones = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "tokyo": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "los angeles": "America/Los_Angeles"
    }

    tz_name = city_timezones.get(city.lower())
    if not tz_name:
        return f"Sorry, I don't know the timezone for {city}."

    tz = pytz.timezone(tz_name)
    local_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    return {f"{city.title}": local_time}


def get_weather(city: str) -> str:
    """
    Simulate getting the weather for a given city.

    Args:
        city (str): Name of the city.

    Returns:
        str: Weather information.
    """
    print("[TOOL] WEATHER invoked")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(
            f"https://search.brave.com/search?q=météo+à+{city}&source=desktop",
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException:
        return "Sorry, I couldn't fetch search results at this time."

    soup = BeautifulSoup(response.text, "html.parser")
    snippet = soup.find("div")

    if snippet and snippet.get_text(strip=True):
        return snippet.get_text(strip=True)
    return "No results found for your query."


def web_search(query: str) -> str:
    """
    Perform a simple web search and return the top snippet.

    Args:
        query (str): Search query.

    Returns:
        str: Snippet from search results.
    """
    print("[TOOL] WEB_SEARCH invoked")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(
            f"https://search.brave.com/search?q={query}&source=desktop",
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException:
        return "Sorry, I couldn't fetch search results at this time."

    soup = BeautifulSoup(response.text, "html.parser")
    snippet = soup.find("div")

    if snippet and snippet.get_text(strip=True):
        return snippet.get_text(strip=True)
    return "No results found for your query."
