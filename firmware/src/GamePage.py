import displayio
import time
from Page import Page

class GamePage(Page):
    def __init__(self, header, fps, screen_width=240):
        super().__init__(header_text=header)
        self.inGame = False
        self.otherIdleUpdates = True
        self.ignore_sensor = True

        self.last_update = time.monotonic()
        self.fps = fps

        bmp = displayio.OnDiskBitmap("graphics/joystick.bmp")
        self.indicator_tilegrid = displayio.TileGrid(
            bmp,
            pixel_shader=bmp.pixel_shader,
            x=screen_width - 75,
            y=4,
        )
        self.indicator_tilegrid.hidden = True
        self.group.append(self.indicator_tilegrid)

    def _set_in_game(self, value):
        self.inGame = value
        self.indicator_tilegrid.hidden = not value

    def on_show(self):
        self.store.set_active_metric(None)

    def on_short_select(self):
        if not self.inGame: # first press just enters the game
            self._set_in_game(True)
            return
        self.game_short_select()

    def on_long_select(self):
        self._set_in_game(not self.inGame)

    def on_short_next(self):
        if self.inGame:
            self.game_short_next()
            return False

    def should_update(self):
        if not self.inGame:
            return False
        return time.monotonic() - self.last_update > (1 / self.fps)

    def update_page(self):
        self.game_update_frame()
        self.last_update = time.monotonic()

    def data_schedule_update(self):
        pass

    def game_short_select(self):
        pass

    def game_short_next(self):
        pass

    def game_update_frame(self):
        pass