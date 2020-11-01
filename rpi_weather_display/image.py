from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
import io


def create_forecast_image(
    hourly_plot,
    daily_text,
    current_text,
    width=1448,
    height=1072,
    rotate=0,
    font_path=None,
):
    """
    Combines the daily, hourly and current weather images and returns a PIL
    image ready to send to the display
    """
    left_indent = 20
    top_indent = 20

    if font_path == None:
        font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")

    img = Image.new("L", (width, height), color=255)

    # Current
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

    # Daily
    indent = left_indent
    d.text(
        (left_indent, 280),
        "W e a t h e r   FUTURE!",
        font=ImageFont.truetype(font_path, 40),
        fill=0,
    )
    for day in daily_text:
        d = ImageDraw.Draw(img)
        d.text((indent, 350), day, font=ImageFont.truetype(font_path, 30), fill=0)
        indent = indent + 200

    # Hourly graph
    img.paste(hourly_plot, (left_indent, 500))

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


def create_error_image(err, width=1448, height=1072, rotate=0, font_path=None):
    """
    Formats an exception into an image to send to the display
    """
    if font_path == None:
        font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")

    img = Image.new("L", (width, height), color=255)
    d = ImageDraw.Draw(img)
    d.text((10, 10), str(err), font=ImageFont.truetype(font_path, 50), fill=0)

    return img.rotate(rotate)
