import io
from PIL import Image, ImageDraw, ImageFont
import pkg_resources
from datetime import datetime


import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Set DPI
plt.rcParams['figure.dpi'] = 72


def pretty_print_dictionary(d):
    '''
    '''
    lines = []

    for k, v in d.items():
        if type(v) == float:
            v = round(v, 1)
        lines.append('{0}: {1}'.format(k.capitalize(), v))

    return '\n'.join(lines)


def create_display_image(hourly_plot, daily_text, current_text, width=1448, height=1072, rotate=0, font_path=None):
    '''
    Combines the daily, hourly and current weather images and returns a PIL
    image ready to send to the display
    '''

    # size = (current.width + hourly.width + daily.width, current.height + hourly.height + daily.height)
    # img = Image.new('L', size)
    # img.paste(current, (0, 0))
    # img.paste(hourly, (0, current.height))
    # img.paste(daily, (0, current.height + hourly.height))
    # img = img.rotate(rotate)
    # img = img.resize((width, height))

    if font_path == None:
        font_path = pkg_resources.resource_filename('rpi_weather_display', 'fonts/Roboto-Bold.ttf')

    img = Image.new('L', (width, height), color=255)

    # Current
    d = ImageDraw.Draw(img)
    d.text((5,5), "W e a t h e r   NOW!", font=ImageFont.truetype(font_path, 40), fill=0)
    d.text((5,70), current_text, font=ImageFont.truetype(font_path, 30), fill=0)

    # Daily
    indent = 0
    d.text((5, 270), "W e a t h e r   FUTURE!", font=ImageFont.truetype(font_path, 40), fill=0)
    for day in daily_text:
        d = ImageDraw.Draw(img)
        d.text((indent, 350), day, font=ImageFont.truetype(font_path, 30), fill=0)
        indent = indent + 200


    # Hourly graph
    img.paste(hourly_plot, (0, 500))

    return img.rotate(rotate)


def convert_plt_fig_to_pil(fig):
    '''
    Converts a matplotlib.pyplot figure to a PIL image
    '''
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


def create_current_text(data):
    '''
    '''
    data['updated_at'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    return pretty_print_dictionary(data)


def create_daily_text(data):
    '''
    '''
    days = []
    for d in data:
        if d['time'].date() == datetime.today().date():
            time = 'Today'
        else:
            time = d['time'].strftime("%A")

        days.append(
            f"{time}\nLow: {d['temperature_min']}\nHigh: {d['temperature_max']}\nRain: {d['rain']}"
        )

    return days


def create_hourly_plot(data):
    '''
    '''
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)

    # plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    # plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    # plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=15)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=15)    # fontsize of the tick labels
    # plt.rc('figure', titlesize=BIGGER_SIZE)

    # Resample and interpolate the DataFrame to make lines smooth
    df = df.resample('1T').asfreq()
    df = df.interpolate(method='cubic')

    # Create the plot
    fig=plt.figure(figsize=(20.12, 8))
    ax2 = plt.subplot(211)
    plt.plot(df.index, df["temperature"], color='black', linewidth=10)
    ax1 = plt.subplot(212)
    plt.plot(df.index, df["rain"], color='black', linewidth=10)
    date_form = DateFormatter("%H:%M")
    ax1.xaxis.set_major_formatter(date_form)
    ax2.xaxis.set_major_formatter(date_form)
    fig.tight_layout()

    return fig
