import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io
from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
from datetime import datetime
from matplotlib.dates import DateFormatter


# Set DPI
plt.rcParams["figure.dpi"] = 72

# Set paths for resources
font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")
icon_path = resource_filename("rpi_weather_display", "icons")


def create_forecast_image(
        hourly: Image,
        daily: Image,
        current: Image,
        width: int = 1448,
        height: int = 1072,
        rotate: int = 0,
        color: int = 255,
        font_path: str = None,
    ):
    """
    Combines the daily, hourly and current weather images and returns a PIL
    image ready to send to the display
    """

    img = Image.new("L", (width, height), color=color)
    img.paste(current, (0, 0))
    img.paste(daily, (0, 180))
    img.paste(hourly, (0, 500))

    # Draw separator lines between sections
    d = ImageDraw.Draw(img)
    d.line([(0, 178), (width, 178)], fill=0, width=3)
    d.line([(0, 498), (width, 498)], fill=0, width=3)

    return img.rotate(rotate)


def convert_plt_fig_to_pil(fig):
    """
    Converts a matplotlib.pyplot figure to a PIL image
    """
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


def get_b_and_white_icon(path: str, gb_color: int):
    """
    Returns a PIL image of an PNG icon
    """
    icon_with_alpha = Image.open(path, mode="r")
    icon = Image.new("L", icon_with_alpha.size, color=gb_color)
    icon.paste(icon_with_alpha, (0, 0), mask=icon_with_alpha.split()[3])
    return icon


def create_error_image(
        error_text: str,
        width: int = 1448,
        height: int = 1072,
        rotate: int = 0,
        color: int = 255,
    ):
    """
    Formats an exception into an image to send to the display
    """
    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    d.text((10, 10), f"{time_now}\n{error_text}", font=ImageFont.truetype(font_path, 30), fill=0)

    return img.rotate(rotate)


def create_daily_image(daily_data: list, color: int = 255):
    """
    Creates the image for the daily weather
    """
    width = 1448
    height = 320
    left_indent = 20
    top_indent = 15

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)

    # Section title
    d.text(
        (left_indent, top_indent),
        "FORECAST",
        font=ImageFont.truetype(font_path, 32),
        fill=0,
    )

    col_width = 200
    icon_size = 100  # icons are 100x100 at @2x

    for i, day in enumerate(daily_data):
        x = left_indent + i * col_width

        # Vertical divider between days (skip before first)
        if i > 0:
            d.line([(x - 10, 60), (x - 10, height - 20)], fill=180, width=2)

        if day["time"].date() == datetime.today().date():
            day_name = "Today"
        else:
            day_name = day["time"].strftime("%a")

        # Day name
        d.text(
            (x, 62),
            day_name,
            font=ImageFont.truetype(font_path, 28),
            fill=0,
        )

        # Temp max / min
        d.text(
            (x, 98),
            f"{round(day['temperature_max'])}° / {round(day['temperature_min'])}°",
            font=ImageFont.truetype(font_path, 26),
            fill=0,
        )

        # Rain
        rain_val = round(day["rain"], 1)
        d.text(
            (x, 132),
            f"{rain_val} mm",
            font=ImageFont.truetype(font_path, 24),
            fill=80,
        )

        # Icon — centred within the column
        icon = get_b_and_white_icon(
            "{0}/{1}@2x.png".format(icon_path, day["weather_icon_name"]), color
        )
        icon_x = x + (col_width - icon_size) // 2 - 10
        img.paste(icon, (icon_x, 195))

    return img


def create_current_image(current: dict, provider_name: str, color: int = 255):
    """
    Creates the image for the current weather
    """
    width = 1448
    height = 180
    margin = 28
    update_time = datetime.now().strftime("%H:%M")

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)

    # ── Left block: section label + detail rows ──────────────────────────────
    d.text(
        (margin, 12),
        "NOW",
        font=ImageFont.truetype(font_path, 26),
        fill=80,
    )

    # Hero temperature
    temp_str = f"{round(current['temperature'], 1)}°"
    d.text(
        (margin, 40),
        temp_str,
        font=ImageFont.truetype(font_path, 80),
        fill=0,
    )

    # Feels-like + rain as smaller detail below hero
    detail_x = margin + 200
    d.text(
        (detail_x, 52),
        f"Feels like  {round(current['temperature_feels_like'], 1)}°",
        font=ImageFont.truetype(font_path, 28),
        fill=0,
    )
    d.text(
        (detail_x, 92),
        f"Rain           {round(current['rain'], 1)} mm",
        font=ImageFont.truetype(font_path, 28),
        fill=0,
    )

    # ── Centre block: icon + description ────────────────────────────────────
    icon = get_b_and_white_icon(
        "{0}/{1}@2x.png".format(icon_path, current["weather_icon_name"]), color
    )
    icon_x = 620
    img.paste(icon, (icon_x, 38))

    d.text(
        (icon_x + 115, 62),
        current["description"],
        font=ImageFont.truetype(font_path, 44),
        fill=0,
    )

    # ── Right block: last-updated / provider ────────────────────────────────
    d.text(
        (width - margin - 260, 12),
        f"Updated {update_time}",
        font=ImageFont.truetype(font_path, 22),
        fill=100,
    )
    d.text(
        (width - margin - 260, 40),
        provider_name,
        font=ImageFont.truetype(font_path, 22),
        fill=100,
    )

    return img


def create_hourly_plot(
        data: list, color: int = 255, time_zone_name: str = "Europe/Berlin"
    ):
    """
    Creates the hourly temperature and rain plots
    """
    y_top = max([d["rain"] for d in data]) + 1
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time"] = df["time"].dt.tz_convert(time_zone_name)
    df.set_index("time", inplace=True, drop=True)

    bg = (color / 255,) * 3

    # Set font sizes
    plt.rc("xtick", labelsize=22)
    plt.rc("ytick", labelsize=22)
    plt.rc("axes", labelsize=24)
    plt.rc("figure", facecolor=bg)
    plt.rc("axes", facecolor=bg)

    # Resample and interpolate the DataFrame to make lines smooth
    df = df.resample("1T").asfreq()
    df = df.interpolate(method="cubic")
    df.loc[df.rain < 0, "rain"] = 0

    date_form = DateFormatter("%H:%M", tz=df.index.tz)
    grid_kw = dict(color="#cccccc", linestyle="--", linewidth=2)

    fig, (ax_temp, ax_rain) = plt.subplots(
        2, 1,
        figsize=(20, 7.7),
        facecolor=bg,
        gridspec_kw={"hspace": 0.45},
    )

    # ── Temperature subplot ──────────────────────────────────────────────────
    ax_temp.plot(df.index, df["temperature"], color="black", linewidth=3)
    ax_temp.fill_between(df.index, df["temperature"], df["temperature"].min() - 0.5,
                         color="black", alpha=0.08)
    ax_temp.set_ylabel("°C", labelpad=6)
    ax_temp.grid(**grid_kw)
    ax_temp.xaxis.set_major_formatter(date_form)
    ax_temp.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=4))

    for spine in ["top", "right"]:
        ax_temp.spines[spine].set_visible(False)
    for spine in ["bottom", "left"]:
        ax_temp.spines[spine].set_linewidth(1.5)
        ax_temp.spines[spine].set_color("#888888")

    # ── Rain subplot ─────────────────────────────────────────────────────────
    ax_rain.plot(df.index, df["rain"], color="black", linewidth=3)
    ax_rain.fill_between(df.index, df["rain"], 0, color="black", alpha=0.08)
    ax_rain.set_ylim(bottom=-0.05, top=y_top)
    ax_rain.set_ylabel("mm", labelpad=6)
    ax_rain.grid(**grid_kw)
    ax_rain.xaxis.set_major_formatter(date_form)
    ax_rain.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4))

    for spine in ["top", "right"]:
        ax_rain.spines[spine].set_visible(False)
    for spine in ["bottom", "left"]:
        ax_rain.spines[spine].set_linewidth(1.5)
        ax_rain.spines[spine].set_color("#888888")

    fig.tight_layout()

    return fig
