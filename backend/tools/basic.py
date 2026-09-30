import logging
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SEARCH_URL = "https://search.brave.com/search?q={}&source=desktop"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
REQUEST_TIMEOUT = 5

CITY_TIMEZONES = {
    "new york": "America/New_York",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "los angeles": "America/Los_Angeles",
}


def get_time(city: str) -> str:
    """
    Get the current local time for a given city.

    Args:
        city (str): Name of the city (e.g., "London", "New York").

    Returns:
        str: Current time in that city.
    """
    logger.debug("[TOOL] TIME invoked for %s", city)

    tz_name = CITY_TIMEZONES.get(city.lower())
    if not tz_name:
        return f"Sorry, I don't know the timezone for {city}."

    # `city.title` is a bound method, not a property: the previous code raised
    # AttributeError, so this tool failed on every call.
    local_time = datetime.now(pytz.timezone(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    return f"{city.title()}: {local_time}"


def _search_snippet(query: str) -> str:
    """Fetch a Brave search result page and return a short text snippet."""
    logger.debug("[TOOL] SEARCH invoked for %s", query)

    try:
        response = requests.get(
            SEARCH_URL.format(query),
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.warning("Search request failed for %s", query, exc_info=True)
        return "Sorry, I couldn't fetch search results at this time."

    soup = BeautifulSoup(response.text, "html.parser")
    for selector in ("div.snippet", "div[data-type='web']", "div#results div", "article"):
        snippet = soup.select_one(selector)
        if snippet and snippet.get_text(strip=True):
            return snippet.get_text(strip=True)[:500]

    # Fallback historique : le premier div non vide de la page.
    snippet = soup.find("div")
    if snippet and snippet.get_text(strip=True):
        return snippet.get_text(strip=True)[:500]

    return "No results found for your query."


def get_weather(city: str) -> str:
    """
    Get the current weather for a given city.

    Args:
        city (str): Name of the city.

    Returns:
        str: Weather information.
    """
    return _search_snippet(f"météo à {city}")


def web_search(query: str) -> str:
    """
    Perform a simple web search and return the top snippet.

    Args:
        query (str): Search query.

    Returns:
        str: Snippet from search results.
    """
    return _search_snippet(query)
