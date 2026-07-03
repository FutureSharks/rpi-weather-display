import logging
import time
from datetime import datetime, timezone
import requests


logger = logging.getLogger()

class openmeteo(object):
    """
    An interface to Open-Meteo API
    """
    def __init__(self, lat, long, api_key=None):
        self.provider_name = "Open-Meteo"
        self.cache_age = 120
        self.last_forecast_update = 0
        self.lat = lat
        self.long = long
        self.api_endpoint = "https://api.open-meteo.com/v1/forecast"
        self.hourly_data = None
        self.daily_data = None
        self.current_data = None

    def _get_data(self):
        try:
            params = {
                "latitude": self.lat,
                "longitude": self.long,
                "current": "temperature_2m,apparent_temperature,weather_code",
                "hourly": "temperature_2m,precipitation",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "celsius",
                "timezone": "auto"
            }
            response = requests.get(self.api_endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Open-Meteo API error: {e}")
            raise

    def _map_weather_code(self, code, is_night=False):
        """
        Converts Open-Meteo WMO weather code to icon name and description
        """
        codes = {
            0: ("01", "Clear"),
            1: ("02", "Mostly Clear"),
            2: ("03", "Partly Cloudy"),
            3: ("04", "Overcast"),
            45: ("50", "Foggy"),
            48: ("50", "Foggy"),
            51: ("09", "Light Drizzle"),
            53: ("09", "Drizzle"),
            55: ("09", "Heavy Drizzle"),
            61: ("09", "Light Rain"),
            63: ("10", "Rain"),
            65: ("10", "Heavy Rain"),
            71: ("13", "Light Snow"),
            73: ("13", "Snow"),
            75: ("13", "Heavy Snow"),
            77: ("13", "Snow Grains"),
            80: ("09", "Light Rain Showers"),
            81: ("10", "Rain Showers"),
            82: ("10", "Heavy Rain Showers"),
            85: ("13", "Light Snow Showers"),
            86: ("13", "Heavy Snow Showers"),
            95: ("11", "Thunderstorm"),
            96: ("11", "Thunderstorm with Hail"),
            99: ("11", "Thunderstorm with Heavy Hail"),
        }

        icon_code, description = codes.get(code, ("00", "Unknown"))
        suffix = "n" if is_night else "d"
        return f"{icon_code}{suffix}", description

    def _is_night(self, hour):
        """Check if hour is night time"""
        return hour < 6 or hour > 20

    def update_forcast(self):
        """
        Refreshes the 3 types of forecasts and saves them
        """
        if None in [self.hourly_data, self.daily_data, self.current_data]:
            pass
        elif time.time() - self.last_forecast_update < self.cache_age:
            logger.debug(f"Skipping forecast update as last update was done less than {self.cache_age} seconds ago")
            return

        logger.debug("Updating Open-Meteo forecast")
        data = self._get_data()
        self.current_data = data["current"]
        self.hourly_data = data["hourly"]
        self.daily_data = data["daily"]
        self.last_forecast_update = time.time()

    def get_daily_data(self, days=7):
        """
        Returns a list of daily weather data
        """
        self.update_forcast()

        results = []
        for i in range(min(days, len(self.daily_data["time"]))):
            d = {}
            d["time"] = datetime.strptime(self.daily_data["time"][i], "%Y-%m-%d")
            d["temperature_min"] = self.daily_data["temperature_2m_min"][i]
            d["temperature_max"] = self.daily_data["temperature_2m_max"][i]
            d["weather_icon_name"] = self._map_weather_code(self.daily_data["weather_code"][i], is_night=False)[0]
            d["rain"] = self.daily_data.get("precipitation_sum", [0] * len(self.daily_data["time"]))[i] or 0
            results.append(d)

        return results

    def get_hourly_data(self, hours=24):
        """
        Returns a list of hourly rain and temperature values
        """
        self.update_forcast()

        results = []
        for i in range(min(hours, len(self.hourly_data["time"]))):
            h = {}
            time_str = self.hourly_data["time"][i]
            h["time"] = datetime.strptime(time_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).astimezone(tz=None)
            h["temperature"] = self.hourly_data["temperature_2m"][i]
            h["rain"] = self.hourly_data.get("precipitation", [0] * len(self.hourly_data["time"]))[i] or 0
            results.append(h)

        return results

    def get_current_weather(self):
        """
        Returns a dict of the current weather
        """
        self.update_forcast()

        current_hour = datetime.now().hour
        is_night = self._is_night(current_hour)

        result = {
            "temperature": self.current_data["temperature_2m"],
            "temperature_feels_like": self.current_data["apparent_temperature"],
        }

        icon_name, description = self._map_weather_code(self.current_data["weather_code"], is_night=is_night)
        result["weather_icon_name"] = icon_name
        result["description"] = description
        result["rain"] = 0

        return result
