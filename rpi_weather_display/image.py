import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FormatStrFormatter

# Set DPI
plt.rcParams["figure.dpi"] = 72

# Set paths for resources
font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")
icon_path = resource_filename("rpi_weather_display", "icons")

# Grayscale palette (0 = black, 255 = white) tuned for a 16-level e-ink panel
INK = 0          # primary text / lines
INK_SOFT = 90    # secondary text
INK_FAINT = 120  # captions and axis furniture
RULE = 200       # hairline dividers
PANEL = 255      # background

# Fixed canvas geometry for the 6" HD Waveshare panel (1448 x 1072)
CANVAS_W = 1448
CANVAS_H = 1072
MARGIN = 30

# Vertical bands (must sum to <= CANVAS_H)
HERO_H = 200
DAILY_H = 320
HERO_Y = 0
DAILY_Y = HERO_H + 8
PLOT_Y = DAILY_Y + DAILY_H + 8   # 576
PLOT_H = CANVAS_H - PLOT_Y       # 496

_font_cache = {}


def _font(size: int):
    """Returns a cached truetype font at the given size"""
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(font_path, size)
    return _font_cache[size]


def _text_w(d: ImageDraw.ImageDraw, text: str, font) -> float:
    """Width of a string in the given font"""
    return d.textlength(text, font=font)


def _draw_centered(d: ImageDraw.ImageDraw, cx: int, y: int, text: str, font, fill=INK):
    """Draws text horizontally centered on cx"""
    d.text((cx - _text_w(d, text, font) / 2, y), text, font=font, fill=fill)


def _create_rotated_text(text: str, font_size: int = 30, color: int = INK):
    """
    Returns text rotated 90 degrees
    """
    font = _font(font_size)
    # Measure the real text width using a temporary draw surface
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    text_w = int(tmp.textlength(text, font=font))
    img = Image.new("L", (text_w, int(font_size)), color=PANEL)
    d = ImageDraw.Draw(img)
    d.text((0, 0), text, font=font, fill=color)
    img = img.rotate(90, expand=1)
    return img


def create_forecast_image(
        hourly: Image,
        daily: Image,
        current: Image,
        width: int = CANVAS_W,
        height: int = CANVAS_H,
        rotate: int = 0,
        color: int = PANEL,
        font_path: str = None,
    ):
    """
    Combines the daily, hourly and current weather images and returns a PIL
    image ready to send to the display
    """
    img = Image.new("L", (width, height), color=color)
    img.paste(current, (0, HERO_Y))
    img.paste(daily, (0, DAILY_Y))
    img.paste(hourly, (0, PLOT_Y))

    # Hairline dividers between the three bands
    d = ImageDraw.Draw(img)
    d.line([(MARGIN + 20, DAILY_Y - 4), (width - MARGIN - 20, DAILY_Y - 4)], fill=RULE, width=2)
    d.line([(MARGIN + 20, PLOT_Y - 4), (width - MARGIN - 20, PLOT_Y - 4)], fill=RULE, width=2)

    return img.rotate(rotate)


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
        base: Image = None,
        width: int = CANVAS_W,
        height: int = CANVAS_H,
        rotate: int = 180,
        color: int = PANEL,
    ):
    """
    Formats an exception into an image to send to the display. If `base` is
    given (the last successfully rendered, already-rotated frame), the error
    is painted as a panel over the hourly-plot band instead of replacing the
    whole screen, so the current temperature and daily forecast stay
    readable.
    """
    if base is not None:
        img = base.copy()
        # `base` is already rotated for display, so the hourly band (bottom
        # of the pre-rotation layout) ends up at the top of the screen once
        # rotated 180 degrees.
        if rotate == 180:
            box = (0, 0, width, PLOT_H)
        else:
            box = (0, PLOT_Y, width, height)
    else:
        img = Image.new("L", (width, height), color=color)
        box = (0, 0, width, height)

    d = ImageDraw.Draw(img)

    text_x = box[0] + MARGIN + 240
    text_y = box[1] + MARGIN
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    d.text((text_x, text_y), "Something went wrong", font=_font(44), fill=INK)
    d.text((text_x, text_y + 70), time_now, font=_font(28), fill=INK_SOFT)
    d.text((text_x, text_y + 130), error_text, font=_font(22), fill=INK)

    return img if base is not None else img.rotate(rotate)


def create_current_image(current: dict, provider_name: str, color: int = PANEL):
    """
    Creates the hero band: large current temperature, condition icon and the
    key "now" stats.
    """
    width = CANVAS_W
    height = HERO_H
    update_time = datetime.now().strftime("%H:%M")

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    img.paste(_create_rotated_text("NOW", font_size=26, color=INK_FAINT), (MARGIN - 20, MARGIN))

    # Temperatures, laid out left-to-right so each piece starts right after
    # the actual measured width of the one before it (rather than fixed
    # offsets, which break when the digit counts differ).
    temp_font_size = 160
    fl_font_size = 24
    gap = 16

    temp_text = f"{round(current['temperature'])}°"
    temp_font = _font(temp_font_size)
    temp_text_width = _text_w(d, temp_text, temp_font)
    temp_left_offset = MARGIN + 72
    d.text((temp_left_offset, 10), temp_text, font=temp_font, fill=INK)

    temp_fl_left_offset = temp_left_offset + temp_text_width + gap
    temp_text_fl = f"{round(current['temperature_feels_like'])}°"
    temp_text_fl_width = _text_w(d, temp_text_fl, temp_font)
    d.text((temp_fl_left_offset, 10), temp_text_fl, font=temp_font, fill=INK_SOFT)

    fl_caption_font = _font(fl_font_size)
    fl_caption_text = "Feels\nlike"
    fl_caption_left_offset = temp_fl_left_offset + temp_text_fl_width + gap
    d.text((fl_caption_left_offset - 52, 106), fl_caption_text, font=fl_caption_font, fill=INK_SOFT)
    fl_caption_width = max(
        _text_w(d, line, fl_caption_font) for line in fl_caption_text.split("\n")
    )

    # Condition icon + description, placed just right of the hero number
    icon_x = int(fl_caption_left_offset + fl_caption_width) + gap
    icon = get_b_and_white_icon(
        "{0}/{1}@2x.png".format(icon_path, current["weather_icon_name"]), color
    )
    icon_larger = icon.resize(size=(180, 180))
    img.paste(icon_larger, (icon_x, 15))

    if current["rain"] > 0:
        rain_text = f"{round(current['rain'], 1)} mm rain"
    else:
        rain_text = "No rain"
    d.text((icon_x + 210, 60), f"{current['description']}\n{rain_text}", font=_font(40), fill=INK_SOFT)

    # Right-hand meta block
    d.multiline_text((CANVAS_W - MARGIN, MARGIN), f"Updated {update_time}\nvia {provider_name}", font=_font(24), fill=INK_SOFT, align="right", anchor="ra")

    return img


def create_daily_image(daily_data: list, color: int = PANEL):
    """
    Creates the 7-day forecast strip: one evenly spaced column per day with an
    icon, day name, hi/lo and rain total.
    """
    width = CANVAS_W
    height = DAILY_H

    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    img.paste(_create_rotated_text("NEXT 7 DAYS", font_size=26, color=INK_FAINT), (MARGIN - 20, MARGIN))

    days = 7
    usable = width - (2 * MARGIN) - 60
    col_w = usable / days

    for i, day in enumerate(daily_data):
        cx = int(MARGIN + col_w * (i + 0.5)) + 48


        if day["time"].date() == datetime.today().date():
            day_name = "Today"
        else:
            day_name = day["time"].strftime("%a")

        _draw_centered(d, cx, 24, day_name, _font(30), fill=INK)

        icon = get_b_and_white_icon(
            "{0}/{1}@2x.png".format(icon_path, day["weather_icon_name"]), color
        ).resize(size=(150, 150))
        img.paste(icon, (cx - icon.width // 2, 64))

        hi_lo = f"{round(day['temperature_max'])}° / {round(day['temperature_min'])}°"
        _draw_centered(d, cx, 210, hi_lo, _font(36), fill=INK)

        rain = f"{round(day['rain'], 1)} mm"
        _draw_centered(d, cx, 268, rain, _font(34), fill=INK_SOFT)

    return img


def _style_axis(ax, color):
    """Applies the shared minimal styling to a plot axis"""
    face = (color / 255,) * 3
    ax.set_facecolor(face)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["bottom", "left"]:
        ax.spines[side].set_linewidth(1.5)
        ax.spines[side].set_color((INK_FAINT / 255,) * 3)
    ax.tick_params(colors=(INK_SOFT / 255,) * 3, length=0, pad=10)
    plt.grid(color="#999999", linestyle=":", linewidth=4, axis="both")
    # ax.set_axisbelow(True)


def create_hourly_image(
        df, color: int = PANEL
    ):
    """
    Creates the 24h temperature and rain plots with a clean, minimal style
    """

    width = CANVAS_W
    height = PLOT_H
    ink = (INK / 255,) * 3
    fill = (INK_FAINT / 255,) * 3

    img = Image.new("L", (width, height), color=color)
    # Set top just above the max
    y_top = df["rain"].max() + 1

    # Typographic defaults for the figure
    plt.rc("xtick", labelsize=32)
    plt.rc("ytick", labelsize=32)
    # plt.rc("axes", labelsize=50)
    face = (color / 255,) * 3
    plt.rc("figure", facecolor=face)
    plt.rc("axes", facecolor=face)

    # Resample and interpolate so the lines read smoothly
    df = df.resample("1min").asfreq()
    df = df.interpolate(method="cubic").bfill().ffill()
    df.loc[df.rain < 0, "rain"] = 0
    x = df.index
    t = np.asarray(df["temperature"].values, dtype=float)
    r = np.asarray(df["rain"].values, dtype=float)

    fig = plt.figure(figsize=(19.8, PLOT_H / 73), facecolor=face)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.96, bottom=0.10, hspace=0.10)

    # Temperature
    t_bottom = float(t.min()) - 1
    ax_t = plt.subplot(211)
    ax_t.plot(x, t, color=ink, linewidth=12, solid_capstyle="round")
    ax_t.fill_between(x, t, np.full_like(t, t_bottom), color=(230 / 255,) * 3, zorder=0)
    ax_t.set_xlim(left=x[0], right=x[-1])
    ax_t.set_ylim(bottom=t_bottom)
    _style_axis(ax_t, color)

    # Rain
    ax_r = plt.subplot(212)
    ax_r.set_ylim(bottom=0, top=y_top)
    ax_r.fill_between(x, r, np.zeros_like(r), color=fill, zorder=1)
    ax_r.plot(x, r, color=ink, linewidth=12, solid_capstyle="round")
    ax_r.set_xlim(left=x[0], right=x[-1])
    _style_axis(ax_r, color)

    date_form = DateFormatter("%H:%M", tz=df.index.tz)

    # Temperature axis formatting
    ax_t.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=9))
    ax_t.xaxis.set_major_formatter(date_form)
    ax_t.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, integer=True))
    ax_t.yaxis.set_major_formatter(FormatStrFormatter('%d°'))
    ax_t.xaxis.set_ticklabels([])
    plt.setp(ax_t.get_yticklabels(), fontweight="bold")

    # Rain axis formatting
    ax_r.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=9))
    ax_r.xaxis.set_major_formatter(date_form)
    ax_r.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, integer=True))
    ax_r.yaxis.set_major_formatter(FormatStrFormatter('%d mm'))
    plt.setp(ax_r.get_xticklabels(), fontweight="bold")
    plt.setp(ax_r.get_yticklabels(), fontweight="bold")

    # Convert the plot to ImageDraw
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    plot_img = Image.open(buf)
    img.paste(plot_img, (16, 10))

    # Add labels for the plots
    d = ImageDraw.Draw(img)
    img.paste(_create_rotated_text("NEXT 24 HOURS", font_size=26, color=INK_FAINT), (MARGIN - 20, MARGIN))

    return img
