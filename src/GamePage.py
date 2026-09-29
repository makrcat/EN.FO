import displayio
import time
from Page import Page

class GamePage(Page):
    def __init__(self, header, fps):
        super().__init__(header_text=header)
        self.inGame = False
        self.otherIdleUpdates = True
        self.ignore_sensor = True
        
        self.last_update = time.monotonic()
        self.fps = fps # default

    def on_show(self):
        self.store.set_active_metric(None)

    def on_short_select(self):
        if not self.inGame: # first time, just enter the game
            self.inGame = True
            return
        
        self.game_short_select()

    def on_long_select(self):
        self.inGame = not self.inGame

    def on_short_next(self):
        if self.inGame:
            self.game_short_next()
            return False

    def should_update(self):
        if self.inGame:
            if time.monotonic() - self.last_update > (1 / self.fps):
                return True
        return False
    
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

