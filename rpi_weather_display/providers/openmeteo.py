import logging
import time
from datetime import datetime, timezone
import requests
import pandas as pd


logger = logging.getLogger()

class openmeteo(object):
    """
    An interface to Open-Meteo API
    """

    WEATHER_CODES = {
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

    def __init__(self, lat, long, time_zone_name, api_key=None):
        self.provider_name = "Open-Meteo"
        self.cache_age = 120
        self.last_forecast_update = 0
        self.lat = lat
        self.long = long
        self.time_zone_name = time_zone_name
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
                "timezone": self.time_zone_name
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
        icon_code, description = self.WEATHER_CODES.get(code, ("00", "Unknown"))
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

    def _prepare_hourly_data(self, data):
        """
        Prepares the list of data items into a basic dataframe
        """
        df = pd.DataFrame(data)
        # Does not need TZ adjusted as it comes in local time
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True, drop=True)

        return df

    def get_hourly_data(self, hours=24):
        """
        Returns a list of hourly rain and temperature values for the next 24 hours
        """
        self.update_forcast()

        # Find the current hour index in the hourly data
        # Because "data is returned starting at 00:00 local-time"
        now = datetime.now()
        current_index = 0
        current_hour_time = None
        for i, time_str in enumerate(self.hourly_data["time"]):
            hour_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
            # Find the first hour at or after the current time
            if hour_time.hour >= now.hour or (hour_time.date() > now.date()):
                current_index = i
                current_hour_time = hour_time
                break
        else:
            # If no future hour found, start from the end
            current_index = len(self.hourly_data["time"]) - hours

        results = []
        for i in range(current_index, min(current_index + hours, len(self.hourly_data["time"]))):
            h = {}
            if i == current_index and current_hour_time is not None:
                h["time"] = current_hour_time
            else:
                h["time"] = datetime.strptime(self.hourly_data["time"][i], "%Y-%m-%dT%H:%M")
            h["temperature"] = self.hourly_data["temperature_2m"][i]
            h["rain"] = self.hourly_data["precipitation"][i]
            results.append(h)

        return self._prepare_hourly_data(results)

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
