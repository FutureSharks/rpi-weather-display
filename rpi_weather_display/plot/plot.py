import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Set DPI
plt.rcParams['figure.dpi'] = 72


def create_current_weather(data):
    fig = plt.figure(figsize=(20.12, 4))
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title("Current weather", fontdict={'fontsize': 30})

    table = plt.table(cellText=[list(data.values())],
                          colWidths=[0.1, 0.15, 0.1, 0.08],
                          colLabels=list(data.keys()),
                          loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(2, 2)

    return fig


def create_hourly(data):
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)

    # Resample and interpolate the DataFrame to make lines smooth
    df = df.resample('1T').asfreq()
    df = df.interpolate(method='cubic')

    # Create the plot
    fig=plt.figure(figsize=(20.12, 7))
    ax2 = plt.subplot(211, title='Temperature')
    plt.plot(df.index, df["temperature"], color='red', linewidth=10)
    ax1 = plt.subplot(212, title='Rain')
    plt.plot(df.index, df["rain"], color='blue', linewidth=10)
    date_form = DateFormatter("%H:%M")
    ax1.xaxis.set_major_formatter(date_form)
    ax2.xaxis.set_major_formatter(date_form)

    return fig


def create_daily(data):
    df = pd.DataFrame(data)

    fig = plt.figure(figsize=(20.12, 4))
    ax = fig.add_subplot(111)
    ax.axis('off')

    table = plt.table(cellText=df.values,
                          colWidths=[0.1, 0.15, 0.1, 0.08, 0.1],
                          colLabels=df.columns,
                          loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(2, 2)



    return fig
