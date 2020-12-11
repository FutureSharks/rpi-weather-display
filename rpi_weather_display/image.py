import pandas as pd
import matplotlib.pyplot as plt
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
    err: Exception,
    width: int = 1448,
    height: int = 1072,
    rotate: int = 0,
    color: int = 255,
    font_path: str = None,
):
    """
    Formats an exception into an image to send to the display
    """
    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    d.text((10, 10), str(err), font=ImageFont.truetype(font_path, 50), fill=0)

    return img.rotate(rotate)


def create_daily_image(daily_data: list, color: int = 255):
    """
    Creates the image for the daily weather
    """
    width = 1448
    height = 320
    left_indent = 20
    top_indent = 20

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)

    d.text(
        (left_indent, top_indent),
        "W e a t h e r   FUTURE",
        font=ImageFont.truetype(font_path, 40),
        fill=0,
    )

    indent = left_indent
    for day in daily_data:
        d = ImageDraw.Draw(img)

        if day["time"].date() == datetime.today().date():
            day_name = "Today"
        else:
            day_name = day["time"].strftime("%A")

        text_lines = [
            day_name,
            str(round(day["temperature_max"]))
            + "° / "
            + str(round(day["temperature_min"]))
            + "°",
            "Rain " + str(round(day["rain"], 1)) + "mm",
        ]

        icon = get_b_and_white_icon(
            "{0}/{1}@2x.png".format(icon_path, day["weather_icon_name"]), color
        )
        img.paste(icon, (indent - 10, 173))

        d.text(
            (indent, 80),
            "\n".join(text_lines),
            font=ImageFont.truetype(font_path, 30),
            fill=0,
        )

        indent = indent + 200

    return img


def create_current_image(current: dict, color: int = 255):
    """
    Creates the image for the current weather
    """
    width = 1448
    height = 220
    left_indent = 20
    top_indent = 20

    img = Image.new("L", (width, height), color=color)

    text_lines = [
        "Temperature   " + str(round(current["temperature"], 1)) + "°",
        "Feels like        " + str(round(current["temperature_feels_like"], 1)) + "°",
        "Rain                   " + str(round(current["rain"], 1)) + "mm",
    ]
    text = "\n".join(text_lines)

    d = ImageDraw.Draw(img)
    d.text(
        (left_indent, top_indent),
        "W e a t h e r   NOW",
        font=ImageFont.truetype(font_path, 40),
        fill=0,
    )
    d.text((left_indent, 80), text, font=ImageFont.truetype(font_path, 30), fill=0)

    icon = get_b_and_white_icon(
        "{0}/{1}@2x.png".format(icon_path, current["weather_icon_name"]), color
    )
    img.paste(icon, (400, 50))
    d.text(
        (540, 120),
        current["description"],
        font=ImageFont.truetype(font_path, 30),
        fill=0,
    )

    d.text(
        (1255, 18),
        "Last updated {0}".format(datetime.now().strftime("%H:%M")),
        font=ImageFont.truetype(font_path, 20),
        fill=0,
    )

    return img


def create_hourly_plot(data: list, color: int = 255):
    """
    Creates the hourly temperature and rain plots
    """
    df = pd.DataFrame(data)
    df.set_index("time", inplace=True)

    # Set colours and font sizes
    plt.rc("xtick", labelsize=30)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=30)  # fontsize of the tick labels
    plt.rc('axes', labelsize=30)    # fontsize of the x and y labels
    plt.rc("figure", facecolor=(color / 255,) * 3)
    plt.rc("axes", facecolor=(color / 255,) * 3)

    # Resample and interpolate the DataFrame to make lines smooth
    df = df.resample("1T").asfreq()
    df = df.interpolate(method="cubic")
    df.loc[df.rain < 0, "rain"] = 0

    # Create the plot
    fig = plt.figure(figsize=(20, 8))
    ax2 = plt.subplot(211)
    plt.plot(df.index, df["temperature"], color="black", linewidth=10)
    plt.grid(color="#999999", linestyle="--", linewidth=5)
    plt.ylabel("Celcius")
    ax1 = plt.subplot(212)
    ax1.set_ylim(bottom=-0.05)
    plt.plot(df.index, df["rain"], color="black", linewidth=10)
    plt.grid(color="#999999", linestyle="--", linewidth=5)
    plt.ylabel("Millimeter")
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
