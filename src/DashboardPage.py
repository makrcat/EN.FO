import displayio, terminalio
from my_utilities import *
from Page import Page
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_text import label
from fonts import PRAGATI_22, PRAGATI_42


class TempBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        
        self.append(Rect(0, 0, 122, 84, outline=0xFFFFFF))
        
        self.temp_label = label.Label(
            PRAGATI_42, 
            text="--.-", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0),
            anchored_position=(20, 12), 
            scale=1
        )
        self.hum_label = label.Label(
            PRAGATI_22, 
            text="-- hu", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0),
            anchored_position=(20, 52), 
            scale=1
        )
        self.append(self.temp_label)
        self.append(self.hum_label)
        
        self.gradient = tempGradientObject(xpos=0, ypos=0, width=12, height=84, pc=0.5, 
                                           colorz=[0x0FEFD8, 0xC300FF, 0xFF0000], group=self)
        self.append(Rect(0, 0, 12, 84, outline=0xFFFFFF))
        
        # Axis labels
        self.temp_top_label = label.Label(terminalio.FONT, text='x', color=0xFFFFFF, anchor_point = (0.5, 0.5),
                                          anchored_position=(7, -6), scale=1)
        self.append(self.temp_top_label)
        self.temp_bottom_label = label.Label(terminalio.FONT, text='0', color=0xFFFFFF,  anchor_point = (0.5, 0.5),
                                          anchored_position=(7, 76), scale=1)
        self.append(self.temp_bottom_label)
        
        self.last_temp_unit = None

    def update(self, store):
        temp_con = store.getConvertedVal("temperature")
        temp_unit = store.get_setting("temperature_unit")
        self.temp_label.text = f"{temp_con:.1f}"+ temp_unit
        self.hum_label.text = f"{store.getVal("humidity"):.1f}% hu"
        
        max = 100 if temp_unit == 'F' else (37.8 if temp_unit == 'C' else 310.95)
        min = 32 if temp_unit == 'F' else (0 if temp_unit == 'C' else 273.15)
        self.gradient.update((temp_con - min) / (max - min))
        
        if self.last_temp_unit != temp_unit:
            self.temp_top_label.text = str(max)
            self.temp_bottom_label.text = str(min)
            self.last_temp_unit = temp_unit

class GasBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        
        self.append(Rect(0, 0, 108, 90, outline=0xFFFFFF))
        
        self.aqi_label = label.Label(
            PRAGATI_42, 
            text="--.-", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0),
            anchored_position=(10, 12),
            scale=1
        )

        
        self.resistance_label = label.Label(
            PRAGATI_22, 
            text="--.-", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0), 
            anchored_position=(10, 52),
            scale=1
        )

        self.append(self.aqi_label)
        self.append(self.resistance_label)

        self.gradient = tempGradientObject(
            xpos=4, ypos=78, width=100, height=7,pc=1.0, group=self, 
            colorz=[0x31D726, 0xE6C329, 0xDF752F, 0xDB2424, 0x892ADC], 
            orientation='horizontal'
        )
        
        
        self.pointer_group = displayio.Group()
        pointer_shape = Triangle(0, 4, -4, 0, 4, 0, fill=0xFFFFFF)
        self.pointer_group.append(pointer_shape)
        self.pointer_group.y = 71
        self.pointer_group.x = 4
        self.append(self.pointer_group)
        
        
        self.append(Rect(4, 78, 100, 7, outline=0xFFFFFF))

    def update(self, store):
        aqi = store.getVal("aqi")
        self.aqi_label.text = f"{aqi:.1f}"
        self.resistance_label.text = f"rst: {(store.getVal("gas_resistance")/100):.0f}K"
        
        constrained_aqi = max(0.0, min(aqi, 500.0))
        self.pointer_group.x = 4 + int((constrained_aqi / 500.0) * 100)
        

class AltBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)

        self.alt_label = label.Label(
            PRAGATI_42,
            text="---", 
            color=0xFFFFFF,
            anchor_point=(0.5, 0.0),
            anchored_position=(42, 12 ), 
            scale=1
            )
        self.press_label = label.Label(
            PRAGATI_22, 
            text="----", 
            color=0xFFFFFF, 
            anchor_point=(0.0, 0.0),
            anchored_position=(8, 52),  
            scale=1
        )
        self.append(self.alt_label)
        self.append(self.press_label)

        self.append(Rect(0, 0, 86, 84, outline=0xFFFFFF))
        self._draw_decor()
    
    def _draw_decor(self):
        width = 80
        height = 30

        bitmap = displayio.Bitmap(width, height, 2)
        palette = displayio.Palette(2)
        palette[0] = 0x000000
        palette[1] = 0xFFFFFF
        palette.make_transparent(0)

        for i in range(2):

            bitmaptools.draw_line(bitmap, 0, 15 + i, 35, 0 + i, 1)    # Left side
            bitmaptools.draw_line(bitmap, 35, 0 + i, 70, 15 + i, 1)  # Right side
            
            gap = 6
            
            bitmaptools.draw_line(bitmap, 0, 15 + gap + i, 35, 0 + gap + i, 1)   # Left side
            bitmaptools.draw_line(bitmap, 35, 0 + gap + i, 70, 15 + gap + i, 1)

        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        tile_grid.x = 6
        tile_grid.y = -16
        self.append(tile_grid)

    def update(self, store):
        self.alt_label.text = f"{store.getConvertedVal("altitude"):.0f}" + store.get_setting("measurement_unit")
        self.press_label.text = f"{store.getVal("pressure"):.0f} hPa"
        
            

class LastBox(displayio.Group):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)

        self.append(Rect(0, 0, 100, 90, outline=0xFFFFFF))


class DashboardPage(Page):
    
    def __init__(self, store):
        super().__init__(header_text="ALL data!")
        self.store = store

        self.temp_box = TempBox(x=13, y=40)
        self.alt_box = AltBox(x=143, y=40)
        self.gas_box = GasBox(x=13, y=132)
        self.last_box = LastBox(x=129, y=132)


        self.group.append(self.temp_box)
        self.group.append(self.alt_box)
        self.group.append(self.gas_box)
        self.group.append(self.last_box)
        
        self.headerMomentary = MomentaryText(self.header_label, "-- Logged --", 0.5)
   

    def on_show(self):
        self.store.set_active_metric(None)

    def on_short_select(self):
        pass

    def on_long_select(self):
        temp_str = str(self.store.getConvertedVal("temperature")) + self.store.get_setting("temperature_unit")
        a_str = str(self.store.getConvertedVal("aqi"))
        p_str = str(self.store.getConvertedVal("altitude")) + self.store.get_setting("measurement_unit")
        self.store.rollingLog.add_entry((temp_str, p_str, a_str))
        
        self.headerMomentary.start()

    def on_short_next(self):
        pass

    def update_page(self):
        self.temp_box.update(self.store)
        self.alt_box.update(self.store)
        self.gas_box.update(self.store)
        
        self.headerMomentary.checkForUpdate()

    def data_schedule_update(self):
        pass


