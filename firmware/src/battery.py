import displayio
import terminalio
from adafruit_display_text import label
import bitmaptools

BATTERY_CURVE = [
    (4.20, 100),
    (4.10,  90),
    (4.00,  80),
    (3.90,  70),
    (3.80,  60),
    (3.70,  50),
    (3.60,  40),
    (3.50,  30),
    (3.40,  20),
    (3.20,  10),
    (3.00,   0)
]

class Battery:
    def __init__(self, master_group, display_width):
        # setup palette and bitmap
        self.bat_palette = displayio.Palette(5) 
        self.bat_palette[0] = 0x000000 
        self.bat_palette[1] = 0xFFFFFF
        self.bat_palette[2] = 0x00FFFF
        self.bat_palette[3] = 0xFFA500
        self.bat_palette[4] = 0xFF0000  

        self.bat_bitmap = displayio.Bitmap(22, 10, 5) 
        self.bat_tilegrid = displayio.TileGrid(self.bat_bitmap, pixel_shader=self.bat_palette) 

        self.bat_group = displayio.Group(x=display_width - 28, y=5) 
        self.bat_group.append(self.bat_tilegrid) 
        master_group.append(self.bat_group) 

        # setup percentage
        self.signal = label.Label(
            terminalio.FONT, 
            text="00%", 
            color=0xFFFFFF, 
            anchor_point=(1.0, 0.0),
            anchored_position=(display_width - 28 - 4, 4), 
            scale=1
        )
        master_group.append(self.signal)
        
        # shelll
        self._draw_battery_shell()

    def _better_bitmap_fill(self, x, y, w, h, value):
        bitmaptools.fill_region(self.bat_bitmap, x, y, x+w, y+h, value)

    def _draw_battery_shell(self):
        self.bat_bitmap.fill(0)
        self._better_bitmap_fill(0, 0, 20, 10, value=1)
        self._better_bitmap_fill(20, 2, 2, 6, value=1) 
        self._better_bitmap_fill(1, 1, 18, 8, value=0)

    def _voltage_to_percentage(self, voltage):
        for i in range(len(BATTERY_CURVE) - 1):
            v_high, p_high = BATTERY_CURVE[i]
            v_low, p_low = BATTERY_CURVE[i + 1]
            
            if voltage >= v_low:
                voltage_range = v_high - v_low
                percentage_range = p_high - p_low
                position_over = voltage - v_low
                return int(p_low + (position_over / voltage_range) * percentage_range)
        return 0

    def update(self, voltage=3.6):
        p_100 = self._voltage_to_percentage(voltage)
        self.signal.text = f"{p_100}%"
        
        percentage = p_100 / 100
        
        if percentage > 0.6:
            pcolor = 2
        elif percentage > 0.2:
            pcolor = 3
        else:
            pcolor = 4
        
        width = max(1, int(percentage * 16))
        self._better_bitmap_fill(1, 1, 18, 8, value=0)
        self._better_bitmap_fill(2, 2, width, 6, value=pcolor)