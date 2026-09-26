import displayio
from Page import Page
from adafruit_display_text import label
from fonts import NINE, NINE_BOLD
from theme import LOGGER_BOX_BITMAP, BOX_PALETTE

class LogArea(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        
        ugh = ["temp", "alt", "aqi"]
        header_text = "".join([u.ljust(8) for u in ugh])
        
        self.header = label.Label(
            NINE_BOLD, 
            text=header_text, 
            color=0xFFFF00,
            anchor_point=(0.0, 0.0), 
            anchored_position=(4, 2), 
            line_spacing=1.2,
            scale=1
        )
        self.log_label = label.Label(
            NINE, 
            text="...", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0), 
            anchored_position=(4, 28), 
            line_spacing=1.2,
            scale=1
        )
        
        
        self.bg_grid = displayio.TileGrid(LOGGER_BOX_BITMAP, pixel_shader=BOX_PALETTE)
        self.append(self.bg_grid)
  

        self.append(self.log_label)
        self.append(self.header)
                
    def render(self, store):
        log_lines = ""
        for i in range(store.rollingLog.len()):
            row_data = store.rollingLog.get_row(i)
            this_line = ""
            
            for data in row_data:
                this_line += data.ljust(8)
                
            log_lines += this_line + "\n"
                
        self.log_label.text = log_lines


class LoggerPage(Page):
    def __init__(self, store):
        super().__init__(header_text="Data Log")
        self.store = store
        
        self.log_box = LogArea(x=25, y=40)
        self.log_box.render(self.store)
        self.group.append(self.log_box)
        
        
    def on_show(self):
        self.store.set_active_metric(None)

    def on_short_select(self):
        pass

    def on_long_select(self):
        pass

    def on_short_next(self):
        pass

    def update_page(self):
        pass
        
    def data_schedule_update(self):
        pass