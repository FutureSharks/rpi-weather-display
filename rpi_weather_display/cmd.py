# -*- coding: utf-8 -*-


import argparse
import os
import sys
import time
from rpi_weather_display import (
    create_current_text,
    create_daily_text,
    create_hourly_plot,
    create_forecast_image,
    create_error_image,
    convert_plt_fig_to_pil,
)
from rpi_weather_display.providers import owmWeather
from rpi_weather_display.display import eInkDisplay


def main():
    parser = argparse.ArgumentParser(
        description="A weather display using e-ink screen and a Raspberry Pi"
    )
    parser.add_argument(
        "-a", "--latitude", help="Latitude", default=52.4972531, type=float
    )
    parser.add_argument(
        "-o", "--longitude", help="Longitude.", default=13.4143556, type=float
    )
    parser.add_argument(
        "-v", "--vcom", help="E-ink display VCOM value", default=-2.48, type=float
    )
    parser.add_argument(
        "-r",
        "--refresh",
        help="Refresh frequency for forecast in minutes",
        default=15,
        type=int,
    )
    parser.add_argument("-k", "--api-key", help="OWM API key", type=str, required=True)
    config = parser.parse_args()

    forecast = owmWeather(
        lat=config.latitude, long=config.longitude, api_key=config.api_key
    )
    display = eInkDisplay(vcom=config.vcom)

    try:
        while True:
            try:
                c_text = create_current_text(forecast.get_current_weather())
                d_text = create_daily_text(forecast.get_daily_data())
                h_plot = create_hourly_plot(forecast.get_hourly_data())

                img = create_forecast_image(
                    hourly_plot=convert_plt_fig_to_pil(h_plot),
                    daily_text=d_text,
                    current_text=c_text,
                    rotate=180,
                )

                display.paste_image(img)

            except Exception as err:
                error_img = create_error_image(err=err, rotate=180)
                display.paste_image(error_img)

            time.sleep(config.refresh * 60)

    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
