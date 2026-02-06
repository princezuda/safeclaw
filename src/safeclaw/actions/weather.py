"""
SafeClaw Weather Action - Fetch weather without API keys.

Uses free services:
- wttr.in (default) - Simple, no signup
- Open-Meteo - More detailed, also free
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Default config
DEFAULT_PROVIDER = "wttr"
DEFAULT_UNITS = "imperial"  # or "metric"
DEFAULT_LOCATION = "New York"


async def get_weather_wttr(location: str, units: str = "imperial") -> str:
    """
    Fetch weather from wttr.in - simple, free, no API key.

    Args:
        location: City name or coordinates
        units: "imperial" (F) or "metric" (C)
    """
    # wttr.in format codes: https://github.com/chubin/wttr.in
    # %c = condition icon, %C = condition text, %t = temp, %h = humidity, %w = wind
    unit_param = "u" if units == "imperial" else "m"
    url = f"https://wttr.in/{location}?format=%c+%C:+%t+|+Humidity:+%h+|+Wind:+%w&{unit_param}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

        weather = response.text.strip()
        return f"Weather in {location}:\n{weather}"


async def get_weather_openmeteo(
    location: str,
    units: str = "imperial",
    lat: float | None = None,
    lon: float | None = None,
) -> str:
    """
    Fetch weather from Open-Meteo - free, no API key, more detailed.

    Args:
        location: City name (used for display)
        units: "imperial" (F) or "metric" (C)
        lat: Latitude (if known)
        lon: Longitude (if known)
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # If no coords, geocode the location first
        if lat is None or lon is None:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            geo_resp = await client.get(geo_url)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            if not geo_data.get("results"):
                return f"Could not find location: {location}"

            result = geo_data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            location = result.get("name", location)

        # Fetch current weather
        temp_unit = "fahrenheit" if units == "imperial" else "celsius"
        wind_unit = "mph" if units == "imperial" else "kmh"

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&temperature_unit={temp_unit}&wind_speed_unit={wind_unit}"
        )

        resp = await client.get(weather_url)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        temp = current.get("temperature_2m", "?")
        humidity = current.get("relative_humidity_2m", "?")
        wind = current.get("wind_speed_10m", "?")
        weather_code = current.get("weather_code", 0)

        # Map weather codes to descriptions
        condition = _weather_code_to_text(weather_code)

        temp_symbol = "°F" if units == "imperial" else "°C"
        wind_symbol = "mph" if units == "imperial" else "km/h"

        return (
            f"Weather in {location}:\n"
            f"{condition} | {temp}{temp_symbol}\n"
            f"Humidity: {humidity}% | Wind: {wind} {wind_symbol}"
        )


def _weather_code_to_text(code: int) -> str:
    """Convert WMO weather code to human-readable text."""
    codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Foggy",
        48: "🌫️ Depositing rime fog",
        51: "🌧️ Light drizzle",
        53: "🌧️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "🌨️ Heavy snow",
        77: "🌨️ Snow grains",
        80: "🌧️ Slight rain showers",
        81: "🌧️ Moderate rain showers",
        82: "🌧️ Violent rain showers",
        85: "🌨️ Slight snow showers",
        86: "🌨️ Heavy snow showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with slight hail",
        99: "⛈️ Thunderstorm with heavy hail",
    }
    return codes.get(code, f"Weather code {code}")


async def execute(
    params: dict[str, Any],
    user_id: str,
    channel: str,
    engine: Any,
) -> str:
    """
    Execute weather action.

    Params:
        location: City name (optional, uses default)
        provider: "wttr" or "open-meteo" (optional)
        units: "imperial" or "metric" (optional)
    """
    # Get config from engine
    config = engine.config.get("actions", {}).get("weather", {})

    location = params.get("location") or config.get("default_location", DEFAULT_LOCATION)
    provider = params.get("provider") or config.get("provider", DEFAULT_PROVIDER)
    units = params.get("units") or config.get("units", DEFAULT_UNITS)

    try:
        if provider == "open-meteo":
            return await get_weather_openmeteo(location, units)
        else:
            return await get_weather_wttr(location, units)
    except httpx.HTTPError as e:
        logger.error(f"Weather fetch failed: {e}")
        return f"Could not fetch weather for {location}: {e}"
    except Exception as e:
        logger.error(f"Weather action error: {e}")
        return f"Weather error: {e}"
