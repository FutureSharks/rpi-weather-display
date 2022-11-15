import logging
import time
from datetime import datetime, timezone
import requests


logger = logging.getLogger()

class tomorrow(object):
    """
    An interface to Tomorrow.io API
    """
    def __init__(self, lat, long, api_key):
        self.provider_name = "Tomorrow.io"
        self.lat = lat
        self.long = long
        self.api_key = api_key
        self.api_endpoint = "https://api.tomorrow.io/v4/timelines"
        self.default_query_string = {
            "location": f"{self.lat}, {self.long}",
            "fields": ["temperature"],
            "units": "metric",
            "timesteps": "1d",
            "apikey": self.api_key
        }
        self.hourly_data = None
        self.daily_data = None
        self.current_data = None

    def _get_data(self, query_string):
        try:
            response = requests.request("GET", self.api_endpoint, params=query_string)
            data = response.json()

            if data.get("code", None):
                raise Exception(f"Tomorrow.io API error ({data['code']})): {data['type']}")

            return data
        except requests.JSONDecodeError as e:
            print(e)
            raise
        except Exception as e:
            print(e)
            raise

    def _day_or_night_now(self):
        """
        Simply returns a 'd' or 'n' depending on whether it's day or night right now
        """
        hour = datetime.now(timezone.utc).astimezone().hour
        month = datetime.now(timezone.utc).astimezone().month

        if month in [10, 11, 12, 1, 2, 3]:
            if hour in [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
                return "n"
            else:
                return "d"
        else:
            if hour in [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
                return "n"
            else:
                return "d"

    def _map_daily_weather_icon_name(self, weatherCode):
        """
        Converts Tomorrow.io API 'weatherCodeFullDay' into a PNG file name and description
        """
        if weatherCode == 0:
            code, description = ("00", "Unknown")
        elif weatherCode in [1000]:
            code, description = ("01", "Clear, Sunny")
        elif weatherCode in [1100, 1103]:
            code, description = ("02", "Partly Cloudy")
        elif weatherCode in [1101, 2101, 2102, 2103]:
            code, description = ("03", "Mostly Cloudy")
        elif weatherCode in [1102, 2106]:
            code, description = ("04", "Cloudy")
        elif weatherCode in [1001, 4204, 4203, 4205, 4000, 4200,4213, 4214, 4215, 4209, 4208, 4210]:
            code, description = ("09", "Light Rain")
        elif weatherCode in [4001, 4211, 4202, 4212, 4201, 6000, 6003, 6002, 6004, 6204, 6206, 6205, 6203, 6209, 6200, 6213, 6214, 6215, 6001, 6212, 6220, 6222, 6207, 6202, 6208, 6201]:
            code, description = ("10", "Heavy Rain")
        elif weatherCode in [8001, 8003, 8002, 8000]:
            code, description = ("11", "Thunderstorm")
        elif weatherCode in [5115, 5116, 5117, 5001, 5100, 5102, 5103, 5104, 5122, 5105, 5106, 5107, 5000, 5101, 5119, 5120, 5121, 5110, 5108, 5114, 5112, 7110, 7111, 7112, 7102, 7108, 7107, 7109, 7000, 7105, 7106, 7115, 7117, 7103, 7113, 7114, 7116, 7101]:
            code, description = ("13", "Snow")
        elif weatherCode in [2100, 2000, 2106, 2107, 2108]:
            code, description = ("50", "Fog")
        else:
            raise Exception(f"Uknown weatherCodeFullDay from Tomorrow: {weatherCode}")

        icon_path = f"{code}{self._day_or_night_now()}"

        return icon_path, description

    def _map_current_weather_icon_name(self, weatherCode):
        """
        Converts Tomorrow.io API 'weatherCode' into a PNG file name and description
        """
        if weatherCode == 0:
            code, description = ("00", "Unknown")
        elif weatherCode == 1000:
            code, description = ("01", "Clear, Sunny")
        elif weatherCode == 1100:
            code, description = ("02", "Mostly Clear")
        elif weatherCode == 1101:
            code, description = ("03", "Partly Cloudy")
        elif weatherCode == 1102:
            code, description = ("03", "Mostly Cloudy")
        elif weatherCode == 1001:
            code, description = ("04", "Cloudy")
        elif weatherCode == 2000:
            code, description = ("50", "Fog")
        elif weatherCode == 2100:
            code, description = ("50", "Light Fog")
        elif weatherCode == 4000:
            code, description = ("09", "Drizzle")
        elif weatherCode == 4001:
            code, description = ("10", "Rain")
        elif weatherCode == 4200:
            code, description = ("09", "Light Rain")
        elif weatherCode == 4201:
            code, description = ("10", "Heavy Rain")
        elif weatherCode == 5000:
            code, description = ("13", "Snow")
        elif weatherCode == 5001:
            code, description = ("13", "Flurries")
        elif weatherCode == 5100:
            code, description = ("13", "Light Snow")
        elif weatherCode == 5101:
            code, description = ("13", "Heavy Snow")
        elif weatherCode == 6000:
            code, description = ("09", "Freezing Drizzle")
        elif weatherCode == 6001:
            code, description = ("10", "Freezing Rain")
        elif weatherCode == 6200:
            code, description = ("09", "Light Freezing Rain")
        elif weatherCode == 6201:
            code, description = ("10", "Heavy Freezing Rain")
        elif weatherCode == 7000:
            code, description = ("13", "Ice Pellets")
        elif weatherCode == 7101:
            code, description = ("13", "Heavy Ice Pellets")
        elif weatherCode == 7102:
            code, description = ("13", "Light Ice Pellets")
        elif weatherCode == 8000:
            code, description = ("11", "Thunderstorm")
        else:
            raise Exception(f"Uknown weatherCode from Tomorrow: {weatherCode}")

        icon_path = f"{code}{self._day_or_night_now()}"

        return icon_path, description

    def update_forcast(self):
        """
        Refreshes forecast and saves it
        """
        query_string = self.default_query_string.copy()
        query_string["timesteps"] = "1h"
        query_string["fields"] = ["temperature", "temperatureApparent", "rainIntensity"]
        logger.debug("Updating forecast, getting hourly data")
        self.hourly_data = self._get_data(query_string)

        query_string["timesteps"] = "1d"
        query_string["fields"] = ["temperatureMin", "temperatureMax", "rainIntensity", "weatherCodeFullDay"]
        logger.debug("Updating forecast, getting daily data")
        self.daily_data = self._get_data(query_string)

    def get_daily_data(self, days=7):
        """
        Returns a list of daily weather data
        """
        if self.daily_data == None:
            self.update_forcast()

        results = []

        for day in self.daily_data['data']['timelines'][0]['intervals'][0:days]:
            d = {}
            d["time"] = datetime.strptime(day["startTime"], "%Y-%m-%dT%H:%M:%SZ")
            d["temperature_min"] = day["values"]["temperatureMin"]
            d["temperature_max"] = day["values"]["temperatureMax"]
            d["weather_icon_name"] = self._map_daily_weather_icon_name(day["values"]["weatherCodeFullDay"])[0]
            d["rain"] = day["values"]["rainIntensity"]
            results.append(d)

        return results

    def get_hourly_data(self, hours=24):
        """
        Returns a list of hourly rain and temperature values
        """
        if self.hourly_data == None:
            self.update_forcast()

        results = []

        for hour in self.hourly_data['data']['timelines'][0]['intervals'][0:hours]:
            h = {}
            h["time"] = datetime.strptime(hour["startTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(tz=None)
            h["temperature"] = hour["values"]["temperature"]
            h["rain"] = hour["values"]["rainIntensity"]
            results.append(h)

        return results

    def get_current_weather(self):
        """
        Returns a dict of the current weather
        """
        query_string = self.default_query_string.copy()
        query_string["timesteps"] = "current"
        query_string["fields"] = ["temperature", "temperatureApparent", "rainIntensity", "weatherCode"]
        logger.debug("Updating current data")
        self.current_data = self._get_data(query_string)["data"]["timelines"][0]["intervals"][0]["values"]

        result = {}
        result["temperature"] = self.current_data["temperature"]
        result["temperature_feels_like"] = self.current_data["temperatureApparent"]
        result["weather_icon_name"], result["description"] = self._map_current_weather_icon_name(self.current_data["weatherCode"])
        result["rain"] = self.current_data["rainIntensity"]

        return result
