class Button():
    def __init__(self):
        self._is_pressed = False
        self._was_pressed = False
        self._presses = 0

    def is_pressed(self):
        return self._is_pressed

    def was_pressed(self):
        was_pressed = self._was_pressed
        self._was_pressed = False
        return was_pressed

    def get_presses(self):
        presses = self._presses
        self._presses = 0
        return presses

    def _register_down(self):
        self._is_pressed = True
        self._was_pressed = True
        self._presses += 1

    def _register_up(self):
        self._is_pressed = False

    def _reset(self):
        self.__init__()

    def _get_initial_data(self):
        return self._is_pressed
