class Pixel():
    MAX_BRIGHTNESS = 9

    def __init__(self):
        self._brightness = 0

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, brightness):
        if type(brightness) != int:
            raise TypeError('Brightness must be an integer.')

        if not (0 <= brightness <= self.MAX_BRIGHTNESS):
            raise ValueError('Brightness out of bounds.')

        self._brightness = brightness
