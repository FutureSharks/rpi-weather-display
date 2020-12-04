import logging
from metno_locationforecast import Place, Forecast


logger = logging.getLogger("owmWeather")


class metNorway(object):
    """
    An interface to the Norwegian Meteorological Institute API

    Example:
        home = Place("Berlin", 52.52437, 13.41053, 34)
        forecast = Forecast(home, "github.com/FutureSharks/rpi-weather-display 1.0")
        forecast.update()

    """

    def __init__(self, place_name, lat, long, altitude=0):
        self.place_name = place_name
        self.lat = lat
        self.long = long
        self.altitude = altitude
        self.home = Place(place_name, self.lat, self.long, self.altitude)
        self.forecast = Forecast(
            home, "github.com/FutureSharks/rpi-weather-display 1.0"
        )
        self.forecast.update()

    def get_hourly_data(self, hours=24):
        """
        Returns a list of hourly rain and temperature values
        """
        self.forecast.update()

        results = []

        for hour in forecast.data.intervals[0:hours]:
            h = {
                "date": hour.start_time,
                "air_temperature": hour.variables["air_temperature"].value,
                "precipitation_amount": hour.variables["precipitation_amount"].value,
            }

            results.append(h)

        return results
