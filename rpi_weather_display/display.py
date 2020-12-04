from IT8951.display import AutoEPDDisplay
from IT8951 import constants


class eInkDisplay(object):
    """
    An object to manage the Waveshare e-ink display
    """

    def __init__(self, vcom: float):
        self.display = AutoEPDDisplay(vcom=vcom)
        self.clear_display()
        self.dims = (self.display.width, self.display.height)

    def clear_display(self):
        """
        Clears display by removing any image
        """
        self.display.clear()

    def paste_image(self, img):
        """
        Pastes a PIL image to the display
        """
        self.display.frame_buf.paste(
            0xFF, box=(0, 0, self.display.width, self.display.height)
        )
        paste_coords = [self.dims[i] - img.size[i] for i in (0, 1)]
        self.display.frame_buf.paste(img, paste_coords)
        self.display.draw_full(constants.DisplayModes.GC16)
