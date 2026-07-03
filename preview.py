#!/usr/bin/env python3
"""
Render a preview PNG of the display image using mock data, without any e-ink
hardware. Useful for iterating on the layout in rpi_weather_display/image.py.

Usage:
    python3 preview.py            # writes preview.png next to this script
    python3 preview.py out.png    # writes to a custom path
"""

import math
import os
import sys
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")

from rpi_weather_display.image import (
    create_current_image,
    create_daily_image,
    create_hourly_plot,
    create_forecast_image,
    convert_plt_fig_to_pil,
)


def mock_data():
    current = {
        "temperature": 6.6,
        "temperature_feels_like": 4.2,
        "rain": 0.0,
        "weather_icon_name": "04d",
        "description": "Cloudy",
    }

    icons = ["01d", "02d", "09d", "01d", "13d", "50d", "11d"]
    daily = [
        {
            "time": datetime.today() + timedelta(days=i),
            "temperature_max": 7 - i,
            "temperature_min": 3 - i,
            "rain": round(0.3 * i, 1),
            "weather_icon_name": icons[i],
        }
        for i in range(7)
    ]

    # On-the-hour timestamps so they align to the 1-minute resample grid
    base = datetime.now().replace(minute=0, second=0, microsecond=0).astimezone()
    hourly = [
        {
            "time": base + timedelta(hours=h),
            "temperature": 6 + 2.5 * math.sin(h / 3.0),
            "rain": max(0.0, 0.4 * math.sin(h / 2.0)),
        }
        for h in range(24)
    ]
    return current, daily, hourly


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "preview.png"
    )
    current, daily, hourly = mock_data()

    img = create_forecast_image(
        hourly=convert_plt_fig_to_pil(create_hourly_plot(hourly)),
        daily=create_daily_image(daily),
        current=create_current_image(current, "Tomorrow.io"),
        rotate=0,
    )
    img.save(out)
    print(f"Saved {out} ({img.size[0]}x{img.size[1]}, mode {img.mode})")


if __name__ == "__main__":
    main()
