import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from datetime import datetime
from matplotlib.dates import DateFormatter

# Set DPI
plt.rcParams["figure.dpi"] = 72


def pretty_print_dictionary(d):
    """
    Formats a dictionary for printing on the display
    """
    lines = []

    for k, v in d.items():
        k = k.capitalize()
        k = k.replace("_", " ")
        if type(v) == float:
            v = round(v, 1)
        lines.append("{0}: {1}".format(k, v))

    return "\n".join(lines)


def create_current_text(data):
    """
    Creates the text for the current weather
    """
    data["last_update"] = datetime.now().strftime("%H:%M")

    return pretty_print_dictionary(data)


def create_daily_text(data):
    """
    Creates the text for the daily weather
    """
    days = []
    for d in data:
        if d["time"].date() == datetime.today().date():
            time = "Today"
        else:
            time = d["time"].strftime("%A")

        days.append(
            f"{time}\nLow: {d['temperature_min']}\nHigh: {d['temperature_max']}\nRain: {d['rain']}"
        )

    return days


def create_hourly_plot(data):
    """
    Creates the hourly temperature and rain plots
    """
    df = pd.DataFrame(data)
    df.set_index("time", inplace=True)

    # plt.rc('font', size=20)          # controls default text sizes
    # plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    # plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc("xtick", labelsize=30)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=30)  # fontsize of the tick labels
    # plt.rc('figure', titlesize=BIGGER_SIZE)

    # Resample and interpolate the DataFrame to make lines smooth
    df = df.resample("1T").asfreq()
    df = df.interpolate(method="cubic")
    df.loc[df.rain < 0, 'rain'] = 0

    # Create the plot
    fig = plt.figure(figsize=(20, 8))
    ax2 = plt.subplot(211)
    plt.plot(df.index, df["temperature"], color="black", linewidth=10)
    plt.grid(color="#999999", linestyle="--", linewidth=5)
    ax1 = plt.subplot(212)
    ax1.set_ylim(ymin=-0.05)
    plt.plot(df.index, df["rain"], color="black", linewidth=10)
    plt.grid(color="#999999", linestyle="--", linewidth=5)
    date_form = DateFormatter("%H:%M", tz=df.index.tz)
    ax1.xaxis.set_major_formatter(date_form)
    ax2.xaxis.set_major_formatter(date_form)

    for axis in ["bottom", "left"]:
        ax1.spines[axis].set_linewidth(3)
        ax2.spines[axis].set_linewidth(3)

    for axis in ["top", "right"]:
        ax1.spines[axis].set_linewidth(0)
        ax2.spines[axis].set_linewidth(0)

    fig.tight_layout()

    return fig
