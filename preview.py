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
import random
import sys
from datetime import datetime, timedelta

import pandas as pd
import matplotlib
matplotlib.use("Agg")

from rpi_weather_display.image import (
    create_current_image,
    create_daily_image,
    create_hourly_image,
    create_forecast_image,
)


def mock_data():
    current_temp = round(random.uniform(-15.0, 35.0), 1)
    current = {
        "temperature": current_temp,
        "temperature_feels_like": round(current_temp + random.uniform(-6.0, 6.0), 1),
        "rain": round(max(0.0, random.uniform(-2.0, 5.0)), 1),
        "weather_icon_name": "04d",
        "description": "Cloudy",
    }

    icons = ["01d", "02d", "09d", "01d", "13d", "50d", "11d"]
    daily = []
    for i in range(7):
        temp_max = round(random.uniform(-20.0, 40.0), 1)
        temp_min = round(temp_max - random.uniform(2.0, 15.0), 1)
        daily.append(
            {
                "time": datetime.today() + timedelta(days=i),
                "temperature_max": temp_max,
                "temperature_min": temp_min,
                "rain": round(max(0.0, random.uniform(-3.0, 10.0)), 1),
                "weather_icon_name": random.choice(icons),
            }
        )

    # On-the-hour timestamps so they align to the 1-minute resample grid
    base = datetime.now().replace(minute=0, second=0, microsecond=0).astimezone()
    amplitude = random.uniform(5.0, 25.0)
    midpoint = random.uniform(-10.0, 30.0)
    phase = random.uniform(0, 2 * math.pi)
    hourly = [
        {
            "time": base + timedelta(hours=h),
            "temperature": round(midpoint + amplitude * math.sin(h / 3.0 + phase), 1),
            "rain": round(max(0.0, random.uniform(-1.0, 6.0) * math.sin(h / 2.0)), 1),
        }
        for h in range(24)
    ]
    return current, daily, hourly


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "preview.png"
    )
    current, daily, hourly = mock_data()

    # Convert hourly list to DataFrame (same format as providers return)
    hourly_df = pd.DataFrame(hourly)
    hourly_df["time"] = pd.to_datetime(hourly_df["time"])
    hourly_df.set_index("time", inplace=True)

    img = create_forecast_image(
        hourly=create_hourly_image(hourly_df),
        daily=create_daily_image(daily),
        current=create_current_image(current, "Tomorrow.io"),
        rotate=0,
    )
    img.save(out)
    print(f"Saved {out} ({img.size[0]}x{img.size[1]}, mode {img.mode})")


if __name__ == "__main__":
    main()
