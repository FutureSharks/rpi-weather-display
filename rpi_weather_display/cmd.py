# -*- coding: utf-8 -*-


import argparse
import sys
import time
from rpi_weather_display import (
    create_hourly_plot,
    create_forecast_image,
    create_error_image,
    create_current_image,
    create_daily_image,
    convert_plt_fig_to_pil,
)
from rpi_weather_display.providers import owmWeather, tomorrow
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
        "-t",
        "--time-zone-name",
        help="Time zone name.",
        default="Europe/Berlin",
        type=str,
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
    parser.add_argument(
        "-p",
        "--provider",
        help="Weather provider. Can be 'tomorrow' or 'openweather'.",
        default="tomorrow",
        type=str,
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Weather provider API key",
        type=str,
        required=True
    )

    config = parser.parse_args()

    if config.provider == "tomorrow":
        forecast = tomorrow(
            lat=config.latitude, long=config.longitude, api_key=config.api_key
        )
    elif config.provider == "openweather":
        forecast = owmWeather(
            lat=config.latitude, long=config.longitude, api_key=config.api_key
        )
    else:
        print(f"Unknown weather provider {config.provider}")
        sys.exit(1)

    display = eInkDisplay(vcom=config.vcom)

    try:
        while True:
            try:
                c_image = create_current_image(forecast.get_current_weather(), forecast.provider_name)
                d_image = create_daily_image(forecast.get_daily_data())
                h_plot = create_hourly_plot(
                    forecast.get_hourly_data(), time_zone_name=config.time_zone_name
                )

                img = create_forecast_image(
                    hourly=convert_plt_fig_to_pil(h_plot),
                    daily=d_image,
                    current=c_image,
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
