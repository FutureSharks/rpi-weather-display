import io
from PIL import Image


def create_display_image(current, hourly, daily, width=1448, height=1072, rotate=0):
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

    img = Image.new('RGB', (width, height))
    img.paste(current, (0, 0))
    img.paste(hourly, (0, current.height))
    img.paste(daily, (0, current.height + hourly.height))

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
