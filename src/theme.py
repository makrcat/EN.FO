import displayio
import bitmaptools

BOX_PALETTE = displayio.Palette(2)
BOX_PALETTE[0] = 0x444444
BOX_PALETTE[1] = 0xFFFFFF

# Small Box (68x42)
SMALL_BOX_BITMAP = displayio.Bitmap(68, 42, 2)
bitmaptools.fill_region(SMALL_BOX_BITMAP, 0, 0, 68, 42, 1)
bitmaptools.fill_region(SMALL_BOX_BITMAP, 1, 1, 67, 41, 0)

# small x2 + 5
TX_BOX_BITMAP = displayio.Bitmap(141, 42, 2)
bitmaptools.fill_region(TX_BOX_BITMAP, 0, 0, 141, 42, 1)
bitmaptools.fill_region(TX_BOX_BITMAP, 1, 1, 140, 41, 0)

# Desc Box (86x90)
DESC_BOX_BITMAP = displayio.Bitmap(86, 90, 2)
bitmaptools.fill_region(DESC_BOX_BITMAP, 0, 0, 86, 90, 1)
bitmaptools.fill_region(DESC_BOX_BITMAP, 1, 1, 85, 89, 0)
 
# # big box i guess (if need to use)
# BIG_BOX_BITMAP = displayio.Bitmap(180, 180, 2)
# bitmaptools.fill_region(BIG_BOX_BITMAP, 0, 0, 180, 180, 1)
# bitmaptools.fill_region(BIG_BOX_BITMAP, 1, 1, 179, 179, 0)

# Just for the logger
LOGGER_BOX_BITMAP = displayio.Bitmap(180, 180, 2)
bitmaptools.fill_region(LOGGER_BOX_BITMAP, 0, 0, 180, 180, 1)
bitmaptools.fill_region(LOGGER_BOX_BITMAP, 1, 1, 179, 179, 0)
bitmaptools.fill_region(LOGGER_BOX_BITMAP, 0, 24, 180, 25, 1)