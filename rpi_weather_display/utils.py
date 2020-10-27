import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
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
    fig=plt.figure(figsize=(20, 8))
    ax2 = plt.subplot(211)
    plt.plot(df.index, df["temperature"], color='black', linewidth=10)
    ax1 = plt.subplot(212)
    plt.plot(df.index, df["rain"], color='black', linewidth=10)
    date_form = DateFormatter("%H:%M")
    ax1.xaxis.set_major_formatter(date_form)
    ax2.xaxis.set_major_formatter(date_form)
    fig.tight_layout()

    return fig
