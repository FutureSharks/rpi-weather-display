from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
import io


def create_forecast_image(
    hourly: Image,
    daily: Image,
    current: Image,
    width: int=1448,
    height: int=1072,
    rotate: int=0,
    color: int=255,
    font_path: str=None,
):
    """
    Combines the daily, hourly and current weather images and returns a PIL
    image ready to send to the display
    """

    img = Image.new("L", (width, height), color=color)
    img.paste(current, (0, 0))
    img.paste(daily, (0, 250))
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


def create_error_image(
    err: Exception,
    width: int=1448,
    height: int=1072,
    rotate: int=0,
    color: int=255,
    font_path: str=None,
):
    """
    Formats an exception into an image to send to the display
    """
    if font_path == None:
        font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    d.text((10, 10), str(err), font=ImageFont.truetype(font_path, 50), fill=0)

    return img.rotate(rotate)


def create_daily_image(daily_text: list, font_path: str = None, color: int=255):
    """
    Creates the image for the daily weather
    """
    width=1448
    height=300
    left_indent = 20
    top_indent = 20

    if font_path == None:
        font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)

    d.text(
        (left_indent, top_indent),
        "W e a t h e r   FUTURE!",
        font=ImageFont.truetype(font_path, 40),
        fill=0,
    )

    indent = left_indent
    for day in daily_text:
        d = ImageDraw.Draw(img)
        d.text((indent, 80), day, font=ImageFont.truetype(font_path, 30), fill=0)
        indent = indent + 200

    return img


def create_current_image(current_text: str, font_path: str = None, color: int=255):
    """
    Creates the image for the current weather
    """
    width=1448
    height=300
    left_indent = 20
    top_indent = 20

    if font_path == None:
        font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")

    img = Image.new("L", (width, height), color=color)

    d = ImageDraw.Draw(img)
    d.text(
        (left_indent, top_indent),
        "W e a t h e r   NOW!",
        font=ImageFont.truetype(font_path, 40),
        fill=0,
    )
    d.text(
        (left_indent, 80), current_text, font=ImageFont.truetype(font_path, 30), fill=0
    )

    return img
