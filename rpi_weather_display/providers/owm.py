import logging
import time
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from datetime import datetime, timezone


logger = logging.getLogger("owmWeather")


class owmWeather(object):
    """
    An interface to OpenWeatherMap API
    """

    def __init__(self, lat, long, api_key):
        self.lat = lat
        self.long = long
        self.owm = OWM(api_key)
        self.mgr = self.owm.weather_manager()
        self.update_forcast()

    def update_forcast(self):
        """
        Refreshes forecast
        """
        if (
            not hasattr(self, "one_call")
            or time.time() - self.one_call.current.to_dict()["reference_time"] > 300
        ):
            logger.debug("Updating forecast")
            self.one_call = self.mgr.one_call(lat=self.lat, lon=self.long)
        else:
            return

    def get_daily_data(self, days=7):
        """
        Returns a list of daily weather data
        """
        self.update_forcast()

        results = []

        for day in self.one_call.forecast_daily[0:days]:
            d = {}

            d["time"] = datetime.utcfromtimestamp(day.to_dict()["reference_time"])
            d["temperature_min"] = day.temperature("celsius")["min"]
            d["temperature_day"] = day.temperature("celsius")["day"]
            d["temperature_max"] = day.temperature("celsius")["max"]

            if "all" in day.rain:
                d["rain"] = day.rain["all"]
            else:
                d["rain"] = 0

            results.append(d)

        return results

    def get_hourly_data(self, hours=24):
        """
        Returns a list of hourly rain and temperature values
        """
        self.update_forcast()

        results = []

        for hour in self.one_call.forecast_hourly[0:hours]:
            h = {}

            h["time"] = (
                datetime.utcfromtimestamp(hour.to_dict()["reference_time"])
                .replace(tzinfo=timezone.utc)
                .astimezone(tz=None)
            )
            h["temperature"] = hour.temperature("celsius")["temp"]

            if "1h" in hour.rain:
                h["rain"] = hour.rain["1h"]
            else:
                h["rain"] = 0

            results.append(h)

        return results

    def get_current_weather(self):
        """
        Returns a dict of the current weather
        """
        self.update_forcast()

        current = {
            "temperature": self.one_call.current.temperature("celsius")["temp"],
            "temperature_feels_like": self.one_call.current.temperature("celsius")[
                "feels_like"
            ],
            "description": self.one_call.current.detailed_status,
        }

        if "1h" in self.one_call.current.rain:
            current["rain"] = self.one_call.current.rain["1h"]
        else:
            current["rain"] = 0

        return current
