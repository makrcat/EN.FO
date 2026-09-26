import displayio
from Page import Page
from adafruit_display_text import label
from fonts import NINE

class LogArea(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        
        self.log_label = label.Label(
            NINE, 
            text="...", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0), 
            anchored_position=(0, 0), 
            line_spacing=1.2,
            scale=1
        )
        self.append(self.log_label)
                
    def render(self, store):
        
        log_lines = []
        for i in range(store.rollingLog.len()):
            row_data = store.rollingLog.get_row(i)
            log_lines.append(str(row_data))
                
        self.log_label.text = "\n".join(log_lines)


class LoggerPage(Page):
    def __init__(self, store):
        super().__init__(header_text="System Log")
        self.store = store
        
        self.log_box = LogArea(x=14, y=40)
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