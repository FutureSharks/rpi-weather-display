import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter


# Set DPI
plt.rcParams["figure.dpi"] = 72

# Set paths for resources
font_path = resource_filename("rpi_weather_display", "fonts/Roboto-Bold.ttf")
icon_path = resource_filename("rpi_weather_display", "icons")

# Grayscale palette (0 = black, 255 = white) tuned for a 16-level e-ink panel
INK = 0          # primary text / lines
INK_SOFT = 90    # secondary text
INK_FAINT = 150  # captions and axis furniture
RULE = 200       # hairline dividers
PANEL = 255      # background

# Fixed canvas geometry for the 6" HD Waveshare panel (1448 x 1072)
CANVAS_W = 1448
CANVAS_H = 1072
MARGIN = 40

# Vertical bands (must sum to <= CANVAS_H)
HERO_H = 228
DAILY_H = 332
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


def _draw_right(d: ImageDraw.ImageDraw, right: int, y: int, text: str, font, fill=INK):
    """Draws text right-aligned to the x coordinate `right`"""
    d.text((right - _text_w(d, text, font), y), text, font=font, fill=fill)


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
    d.line([(MARGIN, DAILY_Y - 4), (width - MARGIN, DAILY_Y - 4)], fill=RULE, width=2)
    d.line([(MARGIN, PLOT_Y - 4), (width - MARGIN, PLOT_Y - 4)], fill=RULE, width=2)

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
        width: int = CANVAS_W,
        height: int = CANVAS_H,
        rotate: int = 0,
        color: int = PANEL,
    ):
    """
    Formats an exception into an image to send to the display
    """
    img = Image.new("L", (width, height), color=color)
    d = ImageDraw.Draw(img)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    d.text((MARGIN, MARGIN), "Something went wrong", font=_font(44), fill=INK)
    d.text((MARGIN, MARGIN + 70), time_now, font=_font(28), fill=INK_SOFT)
    d.text((MARGIN, MARGIN + 130), error_text, font=_font(22), fill=INK)

    return img.rotate(rotate)


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

    # Section label
    d.text((MARGIN, 20), "NOW", font=_font(30), fill=INK_FAINT)

    # Hero temperature
    temp_text = f"{round(current['temperature'])}°"
    d.text((MARGIN - 6, 42), temp_text, font=_font(150), fill=INK)
    temp_w = _text_w(d, temp_text, _font(150))

    # Feels-like sits under the hero number
    d.text(
        (MARGIN, 196),
        f"Feels like {round(current['temperature_feels_like'])}°",
        font=_font(30),
        fill=INK_SOFT,
    )

    # Condition icon + description, placed just right of the hero number
    icon_x = int(MARGIN + temp_w + 60)
    icon = get_b_and_white_icon(
        "{0}/{1}@2x.png".format(icon_path, current["weather_icon_name"]), color
    )
    img.paste(icon, (icon_x, 48))
    d.text((icon_x + 168, 98), current["description"], font=_font(56), fill=INK)

    # Right-hand meta block
    right = width - MARGIN
    _draw_right(d, right, 28, "Rain now", _font(28), fill=INK_FAINT)
    _draw_right(d, right, 60, f"{round(current['rain'], 1)} mm", _font(56), fill=INK)
    _draw_right(d, right, 190, f"Updated {update_time}  ·  {provider_name}", _font(24), fill=INK_SOFT)

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

    d.text((MARGIN, 16), "7-DAY FORECAST", font=_font(30), fill=INK_FAINT)

    n = len(daily_data) or 1
    usable = width - 2 * MARGIN
    col_w = usable / n

    for i, day in enumerate(daily_data):
        cx = int(MARGIN + col_w * (i + 0.5))

        if day["time"].date() == datetime.today().date():
            day_name = "Today"
        else:
            day_name = day["time"].strftime("%a")

        _draw_centered(d, cx, 62, day_name, _font(32), fill=INK)

        icon = get_b_and_white_icon(
            "{0}/{1}@2x.png".format(icon_path, day["weather_icon_name"]), color
        )
        img.paste(icon, (cx - icon.width // 2, 100))

        hi_lo = f"{round(day['temperature_max'])}° / {round(day['temperature_min'])}°"
        _draw_centered(d, cx, 258, hi_lo, _font(30), fill=INK)

        rain = f"{round(day['rain'], 1)} mm"
        _draw_centered(d, cx, 296, rain, _font(24), fill=INK_SOFT)

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
    ax.grid(color=(RULE / 255,) * 3, linestyle=":", linewidth=1.4, axis="both")
    ax.set_axisbelow(True)


def create_hourly_plot(
        data: list, color: int = PANEL, time_zone_name: str = "Europe/Berlin"
    ):
    """
    Creates the 24h temperature and rain plots with a clean, minimal style
    """
    y_top = max([d["rain"] for d in data]) + 1
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time"] = df["time"].dt.tz_convert(time_zone_name)
    df.set_index("time", inplace=True, drop=True)

    # Typographic defaults for the figure
    plt.rc("xtick", labelsize=24)
    plt.rc("ytick", labelsize=24)
    plt.rc("axes", labelsize=26)
    face = (color / 255,) * 3
    plt.rc("figure", facecolor=face)
    plt.rc("axes", facecolor=face)

    # Resample and interpolate so the lines read smoothly
    df = df.resample("1min").asfreq()
    df = df.interpolate(method="cubic").bfill().ffill()
    df.loc[df.rain < 0, "rain"] = 0

    import numpy as np
    x = df.index
    t = np.asarray(df["temperature"].values, dtype=float)
    r = np.asarray(df["rain"].values, dtype=float)

    ink = (INK / 255,) * 3
    fill = (INK_FAINT / 255,) * 3

    fig = plt.figure(figsize=(20, PLOT_H / 72), facecolor=face)
    fig.subplots_adjust(left=0.075, right=0.98, top=0.90, bottom=0.10, hspace=0.38)

    # Temperature
    ax_t = plt.subplot(211)
    ax_t.plot(x, t, color=ink, linewidth=4, solid_capstyle="round")
    ax_t.fill_between(x, t, np.full_like(t, float(t.min())),
                      color=(230 / 255,) * 3, zorder=0)
    ax_t.set_ylabel("Temperature °C", color=(INK_SOFT / 255,) * 3)
    ax_t.set_title("NEXT 24 HOURS", loc="left", fontsize=30,
                   color=(INK_FAINT / 255,) * 3, pad=14)
    _style_axis(ax_t, color)

    # Rain
    ax_r = plt.subplot(212)
    ax_r.set_ylim(bottom=0, top=y_top)
    ax_r.fill_between(x, r, np.zeros_like(r), color=fill, zorder=1)
    ax_r.plot(x, r, color=ink, linewidth=3, solid_capstyle="round")
    ax_r.set_ylabel("Rain mm", color=(INK_SOFT / 255,) * 3)
    _style_axis(ax_r, color)

    date_form = DateFormatter("%H:%M", tz=df.index.tz)
    for ax in (ax_t, ax_r):
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=9))
        ax.xaxis.set_major_formatter(date_form)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, integer=True))

    return fig
