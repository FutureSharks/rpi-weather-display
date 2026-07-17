# -*- coding: utf-8 -*-


import argparse
import sys


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
        "-v", "--vcom", help="E-ink display VCOM value", default=-2.89, type=float
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
        help="Weather provider. Can be 'tomorrow', 'openweather', or 'openmeteo'.",
        default="openmeteo",
        type=str,
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Weather provider API key (not required for 'openmeteo')",
        type=str,
        required=False
    )

    config = parser.parse_args()

    import time
    import traceback
    import matplotlib.pyplot as plt
    from rpi_weather_display.image import (
        create_hourly_image,
        create_forecast_image,
        create_error_image,
        create_current_image,
        create_daily_image,
    )
    from rpi_weather_display.providers import owmWeather, tomorrow, openmeteo
    from rpi_weather_display.display import eInkDisplay

    if config.provider == "tomorrow":
        if not config.api_key:
            print("API key is required for 'tomorrow' provider")
            sys.exit(1)
        forecast = tomorrow(
            lat=config.latitude, long=config.longitude, time_zone_name=config.time_zone_name, api_key=config.api_key
        )
    elif config.provider == "openweather":
        if not config.api_key:
            print("API key is required for 'openweather' provider")
            sys.exit(1)
        forecast = owmWeather(
            lat=config.latitude, long=config.longitude, time_zone_name=config.time_zone_name, api_key=config.api_key
        )
    elif config.provider == "openmeteo":
        forecast = openmeteo(
            lat=config.latitude, long=config.longitude, time_zone_name="auto",
        )
    else:
        print(f"Unknown weather provider {config.provider}")
        sys.exit(1)

    display = eInkDisplay(vcom=config.vcom)
    last_good_image = None

    try:
        while True:
            try:
                c_image = create_current_image(forecast.get_current_weather(), forecast.provider_name)
                d_image = create_daily_image(forecast.get_daily_data())
                h_image = create_hourly_image(forecast.get_hourly_data())

                img = create_forecast_image(
                    hourly=h_image,
                    daily=d_image,
                    current=c_image,
                    rotate=180,
                )

                display.paste_image(img)
                last_good_image = img

                plt.close("all")

            except Exception:
                error_img = create_error_image(error_text=traceback.format_exc(), base=last_good_image)
                display.paste_image(error_img)
                print(f"Error: {traceback.format_exc()}")
                time.sleep(300)
                continue

            print("Forecast and display successfully updated")
            time.sleep(config.refresh * 60)

    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
