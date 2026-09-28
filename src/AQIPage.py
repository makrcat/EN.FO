import displayio
from my_utilities import *
from Page import Page
from adafruit_display_text import label
from fonts import NINE, SUBTEN, PRAGATI_54, NINE_BOLD
from theme import SMALL_BOX_BITMAP, TX_BOX_BITMAP, DESC_BOX_BITMAP, BOX_PALETTE
from adafruit_display_shapes.rect import Rect
import gc
import math

STABALIZE_TIME = 1200
class GasOhmsBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)

        self.bg_grid = displayio.TileGrid(SMALL_BOX_BITMAP, pixel_shader=BOX_PALETTE)
        self.append(self.bg_grid)
                
        self.append(label.Label(NINE, text="resistn", color=0xffdf52, anchor_point=(0.0, 0.0), 
                                     anchored_position=(4, 2), scale=1))
        
        self.gas_ohms_label = label.Label(NINE, text="--", color=0xffdf52, anchor_point=(0.0, 0.0), 
                                     anchored_position=(4, 18), scale=1)
        self.append(self.gas_ohms_label)

    def update(self, store):
        self.gas_ohms_label.text = f"{(store.getVal("gas_resistance")/1000):.0f}K"
        
class ConfidenceBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)

        self.bg_grid = displayio.TileGrid(TX_BOX_BITMAP, pixel_shader=BOX_PALETTE)
        self.append(self.bg_grid)
                
        self.append(label.Label(NINE, text="confidence", color=0xFFFFFF, anchor_point=(0.0, 0.0), 
                                     anchored_position=(4, 2), scale=1))   
        
        self.gradient = tempGradientObject(
                    xpos=6, ypos=25, width=100, height=7,pc=0.0, group=self, 
                    colorz=[0xb1d726, 0x4fd726, 0x26d767], 
                    orientation='horizontal'
        )
        
        self.percentage = label.Label(terminalio.FONT, text="x%", color=0xFFFFFF, anchor_point=(0.0, 0.0), 
                                             anchored_position=(110, 23), scale=1)
        self.append(self.percentage) 
        
        self.elapsed_time = label.Label(terminalio.FONT, text="x/x", color=0xFFFFFF, anchor_point=(1.0, 0.0), 
                                                     anchored_position=(141, -16), scale=1)
        self.append(self.elapsed_time) 
        
        self.append(Rect(
            x=self.gradient.xpos - 1,
            y=self.gradient.ypos - 1,
            width=self.gradient.width + 2,
            height=self.gradient.height + 2,
            fill=None,
            outline=0xFFFFFF
        ))
        


    def updateConfidence(self, percent):     
        self.gradient.update(percent)
        self.percentage.text = f"{int(percent * 100)}%"
        
    def updateElapsedTime(self, seconds, store):
        self.elapsed_time.text = f"{seconds}/{store.STABALIZE_TIME}sec"
        
    



class AQIArea(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        self.aqi_label = label.Label(PRAGATI_54, text="--", color=0xFFFFFF, anchor_point=(0.0, 0.0), 
                                     anchored_position=(0, 6), scale=1)
        self.append(self.aqi_label)
        

    def update(self, store):
        self.aqi_label.text = f"{store.getVal('aqi'):.1f}"


def aqi_cat(aqi):
    if aqi <= 50:
        return 0  # Good
    elif aqi <= 100:
        return 1  # Moderate
    elif aqi <= 150:
        return 2  # Unhealthy for Sensitive Groups
    elif aqi <= 200:
        return 3  # Unhealthy
    elif aqi <= 300:
        return 4  # Very Unhealthy
    else:
        return 5  # Hazardous (301 and higher)

pinfo = [
    (
        "Good", 
        "Air quality is pretty good! What a nice day."
    ),
    (
        "Moderate", 
        "Air quality is generally fine, perhaps average."
    ),
    (
        "Okayish", 
        "Air quality is okay, although some people might be sensitive."
    ),
    (
        "Unhealthy", 
        "Some people may experience health effects more than others."
    ),
    (
        "Hazardous", 
        "Be careful. Everyone is likely to experience effects of bad air."
    ),
    (
        "Terrible", 
        "The air is catastrophic, what's happening? Make sure to wear a mask!"
    )
]

class DescriptionBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        
        self.bg_grid = displayio.TileGrid(DESC_BOX_BITMAP, pixel_shader=BOX_PALETTE)
        self.append(self.bg_grid)

        self.header_label = label.Label(
            NINE_BOLD, 
            text="----",
            color=0xEFBA0F, 
            line_spacing=0.8,
            anchor_point=(0.0, 0.0), 
            anchored_position=(5, 3), 
            scale=1
        )
        
        self.description_label = label.Label(
            SUBTEN, 
            text="Loading",
            line_spacing=1.05,
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0), 
            anchored_position=(5, 30), 
            scale=1
        )
        
        self.append(self.header_label)
        self.append(self.description_label)
        
        self.last_cat = None
        
    def update(self, store):
        aqi_val = store.getVal("aqi")
        cat = aqi_cat(aqi_val)
        
        if cat != self.last_cat:
            gc.collect()
            
            self.header_label.text = wrap_text(pinfo[cat][0], 82, NINE_BOLD)
            descy = wrap_pos(self.header_label.text, 25, 35)
            
            self.description_label.text = wrap_text(pinfo[cat][1], 82, SUBTEN)
            self.description_label.anchored_position = (5, descy)
            self.last_cat = cat
    

class AQIPage(Page):
    def __init__(self, store):
        super().__init__(header_text="Air Quality")
        self.store = store

        self.AQI_box = AQIArea(x=14, y=28)
        self.group.append(self.AQI_box)
        
        self.gas_ohms_box = GasOhmsBox(x=14, y=84)
        self.group.append(self.gas_ohms_box)
                
        self.description_box = DescriptionBox(x=142, y=132)
        self.group.append(self.description_box)
        
        self.confidence_box = ConfidenceBox(x=87, y=84)
        self.group.append(self.confidence_box)
        
        
        self.graph_range = 15
        self.graph = DataGraph(xpos=14, ypos=132, width=122, height=90, group=self.group)
        
        self.headerMomentary = MomentaryText(self.header_label, "-- Logged --", 0.5)
        self.timeStarted = 0
        
    def on_show(self):
        self.store.set_active_metric("aqi", self.graph_range)
        self.timeStarted = time.monotonic()

    def on_short_select(self):
        global DATA_RANGE
        current_index = DATA_RANGE.index(self.graph_range)
        next_index = (current_index + 1) % len(DATA_RANGE)
        self.graph_range = DATA_RANGE[next_index]
        
        self.store.resize_active_reading(self.graph_range)

    def on_long_select(self):
        p_str = str(self.store.getConvertedVal("aqi"))
        self.store.rollingLog.add_entry(("-", "-", p_str))
        
        self.headerMomentary.start()

    def on_short_next(self):
        pass 

    def update_page(self):
        self.gas_ohms_box.update(self.store)
        self.AQI_box.update(self.store)
        self.description_box.update(self.store)
        
        gc.collect()

        percent = self.store.getVal("confidence")
        self.confidence_box.updateConfidence(percent)
        
        elapsed = int(time.monotonic() - self.store.start_time)
        self.confidence_box.updateElapsedTime(elapsed, self.store)
        
        self.headerMomentary.checkForUpdate()
            
    def data_schedule_update(self):
        readings = self.store.getVariableData()
        self.graph.draw_the_shit(
            readings.get_data_log(),
            self.store.get_setting("interval"),
            readings.max_samples
        )