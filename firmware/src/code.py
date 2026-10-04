import displayio, digitalio
from my_utilities import *

# import board, busio
from Page import *
from PacManPage import PacManPage


from adafruit_display_shapes.line import Line
from mockIC import MockBME680
import time
from DashboardPage import DashboardPage
from TemperaturePage import TemperaturePage
from PressurePage import PressurePage
from AQIPage import AQIPage
from SettingsPage import SettingsPage
from LoggerPage import LoggerPage
from SnakePage import SnakePage
from battery import Battery
from Game2048Page import Game2048Page

time.sleep(1.0) 
import gc
gc.collect()

displayio.release_displays()

display = None
bme680 = None
next_button = None
select_button = None
battery_pin = None


COMPUTER = True


if COMPUTER:
    import pygame
    from blinka_displayio_pygamedisplay import PyGameDisplay

    display = PyGameDisplay(240, 240)
    display.auto_refresh = False

    bme680 = MockBME680()
    bme680.sea_level_pressure = 1017.9
        


else:
    import board, busio
    from fourwire import FourWire
    import adafruit_bme680
    import adafruit_st7789
    import analogio


    next_button = digitalio.DigitalInOut(board.D3) #14
    next_button.switch_to_input(pull=digitalio.Pull.UP)
    select_button = digitalio.DigitalInOut(board.D6) #26
    select_button.switch_to_input(pull=digitalio.Pull.UP)
    
    battery_pin = analogio.AnalogIn(board.A0)


    i2c_sensor = busio.I2C(
        scl=board.D5,
        sda=board.D4,
        frequency=100_000
    ) #400


    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c_sensor, address=0x77) 
    bme680.sea_level_pressure = 1017.9

    spi = busio.SPI(clock=board.D8, MOSI=board.D10)

    display_bus = FourWire(
        spi, 
        command=board.D9, 
        chip_select=board.D7, 
        reset=None  
    )

    display = adafruit_st7789.ST7789(
        display_bus, 
        width=240, 
        height=240, 
        rowstart=80,
        rotation=180
    )


def get_voltage():
    global battery_pin, COMPUTER
    
    if not COMPUTER:
        pv = battery_pin.value / 65535 * 3.7
        return pv * 2.0
    else:
        return 3.3


data_store = DataStore(bme680)
data_store.load_settings()

### DISPLAY STUFF
master_group = displayio.Group()
display.root_group = master_group


HEADER_HEIGHT = 20
# permanent black background
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000
bg_bitmap = displayio.Bitmap(display.width, display.height, 1)
bg_tilegrid = displayio.TileGrid(bg_bitmap, pixel_shader=color_palette)
bg_line = Line(x0=0, y0=HEADER_HEIGHT, x1=display.width, y1=HEADER_HEIGHT, color=0xFFFFFF)

master_group.append(bg_tilegrid)
master_group.append(bg_line)


# bat group is premanently outside of the content group it's async updated
# do i really know waht async means not really
# its updated silently with other updates
battery_widget = Battery(master_group, display.width)


content_group = displayio.Group()
master_group.append(content_group)



### PAGE ARCHITECTURE ###


PAGE_CLASSES = [
    DashboardPage,
    TemperaturePage,
    PressurePage,
    AQIPage,
    LoggerPage,
    SettingsPage,
    SnakePage,
    PacManPage,
    Game2048Page,
]

page_index = 8
current_page = None
SELECT_DOWN_ON_PRESS = False


def release_page():
    global current_page
    if current_page is None:
        return
    if type(current_page).__name__ == "SettingsPage":
        if current_page.needs_write_update():
            data_store.save_settings()

    while len(content_group) > 0:
        g = content_group[len(content_group) - 1]
        while len(g) > 0:
            g.pop()
        content_group.pop()

    # drop every attribute so nothing is kept alive through the page object
    for name in dir(current_page):
        if not name.startswith("__"):
            try:
                setattr(current_page, name, None)
            except Exception:
                pass
    current_page = None
    
    

def show_page(idx):
    global current_page, SELECT_DOWN_ON_PRESS, COMPUTER

    global current_page, SELECT_DOWN_ON_PRESS
    gc.collect()
    # print("pre-build", gc.mem_free())
    current_page = PAGE_CLASSES[idx](data_store)

    # select behavior depends on the NEW page
    selectDownOnPressPages = ["SnakePage", "PacManPage"]
    SELECT_DOWN_ON_PRESS = type(current_page).__name__ in selectDownOnPressPages

    current_page.on_show()
    content_group.append(current_page.group)

    if not current_page.ignore_sensor:
        current_page.update_page()

    display.refresh()
    gc.collect()
    
    if not COMPUTER: print(type(current_page).__name__, gc.mem_free())

    

def pagers():
    global page_index
    page_index = (page_index + 1) % len(PAGE_CLASSES) 
    show_page(page_index)

def global_init():
    data_store.update()
    show_page(page_index)

global_init()

last_sensor_read = 0 # bug fixed










next_button_pressed_last = False
select_button_pressed_last = False
SMODE = False

NMODE = False
L_SMODE = False
select_time_start_down = 0
long_press_fired = False # prevent the long press always being written True while pressed
long_thresh = 1.5





def handle_buttons_modes():
    global next_button_pressed_last, select_button_pressed_last
    global NMODE, SMODE, L_SMODE, select_time_start_down, long_thresh, long_press_fired
    global SELECT_DOWN_ON_PRESS
    
    next_button_pressed = not next_button.value
    select_button_pressed = not select_button.value

    NMODE = False
    SMODE = False
    L_SMODE = False
    
    if select_button_pressed and not select_button_pressed_last: 
        select_time_start_down = time.monotonic()
        long_press_fired = False
        if SELECT_DOWN_ON_PRESS:
            SMODE = True
        
    elif select_button_pressed:
        if (not long_press_fired) and time.monotonic() - select_time_start_down >= long_thresh:
            L_SMODE = True
            long_press_fired = True
            
    elif (select_button_pressed_last and not select_button_pressed 
          and time.monotonic() - select_time_start_down < long_thresh):
        if not SELECT_DOWN_ON_PRESS:
            SMODE = True
        
    if next_button_pressed and not next_button_pressed_last:
        NMODE = True
        
    next_button_pressed_last = next_button_pressed
    select_button_pressed_last = select_button_pressed
    
# Gemini-generated ####
def handle_buttons_modes_computer():
    global next_button_pressed_last, select_button_pressed_last
    global NMODE, SMODE, L_SMODE, select_time_start_down, long_thresh, long_press_fired
    
    NMODE = False
    SMODE = False
    L_SMODE = False

    # PYGAME window events (handles closing the window properly)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    # Poll keyboard state continuously (similar to reading hardware pins)
    keys = pygame.key.get_pressed()
    next_button_pressed = keys[pygame.K_n] or keys[pygame.K_RIGHT]
    select_button_pressed = keys[pygame.K_s] or keys[pygame.K_RETURN]


    if select_button_pressed and not select_button_pressed_last: 
        select_time_start_down = time.monotonic()
        long_press_fired = False
        if SELECT_DOWN_ON_PRESS:
            SMODE = True
        
    elif select_button_pressed:
        if (not long_press_fired) and time.monotonic() - select_time_start_down >= long_thresh:
            L_SMODE = True
            long_press_fired = True
            
    elif (select_button_pressed_last and not select_button_pressed 
          and time.monotonic() - select_time_start_down < long_thresh):
        
        if not SELECT_DOWN_ON_PRESS: # select if it is after press
            SMODE = True
        

    if next_button_pressed and not next_button_pressed_last:
        NMODE = True
        
    next_button_pressed_last = next_button_pressed
    select_button_pressed_last = select_button_pressed
#########################



last_gc_time = 0
GC_INTERVAL = 1.0
upd = False

while True:

    if COMPUTER: handle_buttons_modes_computer()
    else: handle_buttons_modes()

    now = time.monotonic()

    if now - last_gc_time > GC_INTERVAL:
        #print("Free RAM:", gc.mem_free(), "bytes")
        gc.collect()
        last_gc_time = now
        #print(gc.mem_free(), gc.mem_alloc())
        
    if current_page.otherIdleUpdates:
        upd = current_page.should_update()

    if now - last_sensor_read >= data_store.get_setting("interval"):
        data_store.update()
        
        last_sensor_read = now
        if not current_page.ignore_sensor:
            current_page.data_schedule_update()
            upd = True

    if NMODE:
        if current_page.on_short_next() != False:
            release_page()
            gc.collect()
            pagers()
        else:
            upd = True

    elif SMODE:
        current_page.on_short_select()
        upd = True

    elif L_SMODE:
        current_page.on_long_select()
        upd = True

    if upd:
        current_page.update_page()
        upd = False
        
        battery_widget.update(get_voltage())
        gc.collect()
        display.refresh()

    time.sleep(0.01)
