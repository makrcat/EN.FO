from bitmaptools import Bitmap
from displayio import OnDiskBitmap
import adafruit_imageload
import bitmaptools
import math
import displayio

def blitRect(bitmap: Bitmap, x: int, y: int, width: int, height: int, color: int):
    bitmaptools.fill_region(bitmap, x, y, x + width, y + height, color)
    
def blitPixel(bitmap: Bitmap, x, y, color):
    bitmap[x, y] = color

def load_bitmap_from_file(filename: str) -> Bitmap:
    src, _ = adafruit_imageload.load(
        filename,
        bitmap=displayio.Bitmap,
        palette=displayio.Palette,
    )

    dst = displayio.Bitmap(src.width, src.height, 4)

    for y in range(src.height):
        for x in range(src.width):
            color = src[x, y]

            if color == 0x0000:
                index = 0          # black
            elif color == 0x07E0:
                index = 1          # green
            elif color == 0xF800:
                index = 2          # red
            else:
                index = 3          # gray/other

            dst[x, y] = index

    return dst


def bliBMP(
    dest_bitmap: Bitmap,
    bmp: Bitmap,
    x: int,
    y: int,
    rotation_deg: int,
):
  angle_rads = math.radians(rotation_deg)

  # Shift ox and oy so that (x, y) remains the top-left reference point,
  # but the image rotates around its actual middle.
  center_ox = x + (bmp.width // 2)
  center_oy = y + (bmp.height // 2)

  bitmaptools.rotozoom(
      dest_bitmap,
      bmp,
      ox=center_ox,
      oy=center_oy,
      dest_clip0=(0, 0),
      dest_clip1=(dest_bitmap.width, dest_bitmap.height),
      px=bmp.width // 2,  # Pivot at center X
      py=bmp.height // 2,  # Pivot at center Y
      source_clip0=(0, 0),
      source_clip1=(bmp.width, bmp.height),
      angle=angle_rads,
      scale=1.0,
  )
