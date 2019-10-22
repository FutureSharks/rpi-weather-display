# -*- coding: utf-8 -*-

from rpi_weather_display.providers import owmWeather
from rpi_weather_display.plot import create_hourly, create_daily, create_current_weather
from rpi_weather_display import convert_plt_fig_to_pil, create_display_image
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description='A weather display using e-ink screen and a Raspberry Pi')
    parser.add_argument('-a', '--latitude', help='Latitude', default=52.4972531, type=float)
    parser.add_argument('-o', '--longitude', help='Longitude.', default=13.4143556, type=float)
    parser.add_argument('-v', '--vcom', help='E-ink display VCOM value', default=-2.48, type=float)
    parser.add_argument('-k', '--api-key', help='OWM API key', type=str)
    parser.add_argument('-s', '--save-png', help='Save PNG file instead of writing to display', action='store_true', default=False)
    config = parser.parse_args()

    forecast = owmWeather(lat=config.latitude, lon=config.longitude, api_key=config.api_key)
    display = AutoEPDDisplay(vcom=config.vcom)

    c_plot = create_current_weather(forecast.get_current_weather())
    h_plot = create_hourly(forecast.get_hourly_data())
    d_plot = create_daily(forecast.get_daily_data())

    img = create_display_image(
        hourly_image = convert_plt_fig_to_pil(h_plot),
        daily_image = convert_plt_fig_to_pil(d_plot),
        current_image = convert_plt_fig_to_pil(c_plot)
    )

    display.clear()
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))
    dims = (display.width, display.height)
    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]
    display.frame_buf.paste(img, paste_coords)
    display.draw_full(constants.DisplayModes.GC16)

    sys.exit(0)
