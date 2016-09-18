import math
import time

from .glyphs import get_glyph, blank_column
from .pixel import Pixel


class Display():
    MAX_X = 5
    MAX_Y = 5

    MSG_PIXELS = 'DISPLAY_PIXELS'
    MSG_ON_OFF = 'DISPLAY_ON_OFF'

    def __init__(self):
        self._is_on = True

        self._pixels = []
        for x in range(self.MAX_X):
            self._pixels.append([])
            for y in range(self.MAX_Y):
                self._pixels[x].append(Pixel())

    def get_pixel(self, x, y):
        return self._pixels[x][y].get_brightness()

    def set_pixel(self, x, y, value):
        self._pixels[x][y].set_brightness(value)
        self._send_pixels([format_pixel(x, y, value)])

    def clear(self):
        brightness = 0
        pixels = []
        for x in range(self.MAX_X):
            for y in range(self.MAX_Y):
                self._pixels[x][y].set_brightness(brightness)
                pixels.append(format_pixel(x, y, brightness))
        self._send_pixels(pixels)

    def show(self, image_or_iterable, delay=400, **kwargs):
        # NOTE: Images are not implemented!
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        clear = kwargs.get('clear', False)

        while True:
            for letter in image_or_iterable:
                glyph = get_glyph(letter)
                self._draw_glyph(self._monospace(glyph))
                time.sleep(delay / 1000)

            if not loop:
                break

        if clear:
            self.clear()

    def scroll(self, string, delay=150, **kwargs):
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        monospace = kwargs.get('monospace', False)

        all_glyph = []
        for letter in string:
            glyph = get_glyph(letter)
            all_glyph += (
                self._monospace(glyph) if monospace else glyph + blank_column
            )

        all_glyph_spaced = (
            blank_column * self.MAX_X +
            all_glyph +
            blank_column * self.MAX_X
        )

        while True:
            for index in range(len(all_glyph_spaced) - self.MAX_X + 1):
                self._draw_glyph(all_glyph_spaced[index : index + self.MAX_X])
                time.sleep(delay / 1000)

            if not loop:
                break

    def on(self):
        self._set_on_off(True)

    def off(self):
        self._set_on_off(False)

    def is_on(self):
        return self._is_on

    def _set_on_off(self, is_on):
        self._is_on = is_on
        self._send_message(self.MSG_ON_OFF, {'is_on': self._is_on})

    def _monospace(self, glyph):
        half_diff = (self.MAX_X - len(glyph)) / 2
        return (
            blank_column * math.floor(half_diff) +
            glyph +
            blank_column * math.ceil(half_diff)
        )

    def _draw_glyph(self, glyph):
        pixels = []
        for x, column in enumerate(glyph):
            for y, char in enumerate(column):
                brightness = 9 if char == '#' else 0
                self._pixels[x][y].set_brightness(brightness)
                pixels.append(format_pixel(x, y, brightness))
        self._send_pixels(pixels)

    def _reset(self):
        self.__init__()

    def _get_initial_data(self):
        pixels = []
        for x in range(self.MAX_X):
            for y in range(self.MAX_Y):
                brightness = self._pixels[x][y].get_brightness()
                pixels.append(format_pixel(x, y, brightness))
        return {
            'pixels': pixels,
            'is_on': self._is_on,
        }

    def _send_pixels(self, pixels):
        self._send_message(self.MSG_PIXELS, {'pixels': pixels})

    def _send_message(self, message_name, data):
        print('Display _send_message', message_name, data)


def format_pixel(x, y, brightness):
    return ((x, y), brightness)
