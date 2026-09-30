import displayio
import random
from adafruit_display_text import label
from fonts import NINE_BOLD
from GamePage import GamePage
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
import time, bitmaptools

class MemoryNumber:
    def __init__(self, number, x, y):
        self.number = number
        self.ix = x
        self.iy = y
        self.ox = x
        self.oy = y

    def update_old(self):
        self.ox = self.ix
        self.oy = self.iy

class Game2048Page(GamePage):
    def __init__(self, store):
        super().__init__(header="2048 Game", fps=30)
        
        self.width = 4
        self.height = 4
        self.store = store
        self.scale = 40
        
        boardx = 40
        boardy = 50
        self.boardx = boardx
        self.boardy = boardy
    
        # OUTLINE stuff for the ui
        self.outline = Rect(
            x=boardx - 1, 
            y=boardy - 1, 
            width=self.width * self.scale + 2, 
            height=self.height * self.scale + 2,
            fill=None, 
            outline=0xFFFFFF
        )
        self.group.append(self.outline)
        
        # ARROWS stuff
        center = displayio.Group()
        center.x = self.boardx + self.width * self.scale // 2
        center.y = self.boardy + self.height * self.scale // 2
        
        arrow_offset = 90
        
        self.arrowUp = Triangle(0, -arrow_offset - 5, -5, -arrow_offset, 5, -arrow_offset, fill=0xFFFFFF)
        self.arrowDown = Triangle(0, arrow_offset + 5, -5, arrow_offset, 5, arrow_offset, fill=0xFFFFFF)
        self.arrowLeft = Triangle(-arrow_offset - 5, 0, -arrow_offset, -5, -arrow_offset, 5, fill=0xFFFFFF)
        self.arrowRight = Triangle(arrow_offset + 5, 0, arrow_offset, -5, arrow_offset, 5, fill=0xFFFFFF)

        center.append(self.arrowLeft)
        center.append(self.arrowUp)
        center.append(self.arrowDown)
        center.append(self.arrowRight)
        self.group.append(center)

        self.palette = displayio.Palette(14)
        
        self.palette[0] = 0x111111  # Background / empty
        self.palette[1] = 0xEEE4DA  # 2
        self.palette[2] = 0xEDE0C8  # 4
        self.palette[3] = 0xF2B179  # 8
        self.palette[4] = 0xF59563  # 16
        self.palette[5] = 0xF67C5F  # 32
        self.palette[6] = 0xF65E3B  # 64
        self.palette[7] = 0xEDCF72  # 128
        self.palette[8] = 0xEDCC61  # 256
        self.palette[9] = 0xEDC850  # 512
        self.palette[10] = 0xEDC53F # 1024
        self.palette[11] = 0xEDC22E # 2048
        self.palette[12] = 0x111111 # light tiles text color
        self.palette[13] = 0xFFFFFF # dark tiles text color

        # Create tile graphics sheet
        num_tile_types = 12
        tilesheet_width = self.scale * num_tile_types
        tilesheet_height = self.scale
        self.tilesheet = displayio.Bitmap(tilesheet_width, tilesheet_height, 14)
        
        tile_values = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
        for idx, val in enumerate(tile_values):
            x_offset = idx * self.scale
            color_idx = self.val_to_palette_index(val)
            
            bitmaptools.fill_region(self.tilesheet, x_offset, 0, x_offset + self.scale, self.scale, color_idx)
            
            if val != 0:
                text = str(val)
                text_color = 12 if val <= 4 else 13
                text_x = x_offset + 15
                text_y = 26
                self.draw_text_direct(self.tilesheet, text, NINE_BOLD, text_x, text_y, text_color)

        # Single canvas setup for old-school bitmap blitting/interpolation
        self.canvas_width = self.width * self.scale
        self.canvas_height = self.height * self.scale
        self.canvas_bitmap = displayio.Bitmap(self.canvas_width, self.canvas_height, 14)
        
        self.canvas_grid = displayio.TileGrid(
            self.canvas_bitmap,
            pixel_shader=self.palette
        )

        self.board_group = displayio.Group(x=boardx, y=boardy)
        self.board_group.append(self.canvas_grid)
        self.group.append(self.board_group)

        # Initialize board with MemoryNumber objects
        self.board_array = [[MemoryNumber(0, x, y) for x in range(4)] for y in range(4)]
        self.score = 0
        self.spawn_new_numbers = [2, 4]
        self.directions = ["right", "up", "left", "down"]
        self.arrows = [self.arrowRight, self.arrowUp, self.arrowLeft, self.arrowDown]
        self.direction_index = 0
        self.curframe = 10
        self.max_frame = 10
        self.setActiveArrow(self.direction_index)
        
        self.game_reset()

    def game_reset(self):
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                tile.number = 0
                tile.ix = x
                tile.iy = y
                tile.ox = x
                tile.oy = y
        self.score = 0
        self.spawn_number()
        self.spawn_number()
        self.draw_stuff()
        
    def spawn_number(self):
        empty_tiles = [(x, y) for y in range(4) for x in range(4) if self.board_array[y][x].number == 0]
        if empty_tiles:
            rx, ry = random.choice(empty_tiles)
            tile = self.board_array[ry][rx]
            tile.number = random.choice(self.spawn_new_numbers)
            tile.ix = rx
            tile.iy = ry
            tile.ox = rx
            tile.oy = ry

    def val_to_palette_index(self, val):
        if val == 0:
            return 0
        index = 0
        while val > 1:
            val //= 2
            index += 1
        return min(index, 11)

    def update_all_olds(self):
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                tile.update_old()
                tile.ix = x
                tile.iy = y
                tile.ox = x
                tile.oy = y

    def col_squash_empty_spaces(self, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                if self.board_array[i+1][col].number == 0 and self.board_array[i][col].number != 0:
                    t1 = self.board_array[i][col]
                    t2 = self.board_array[i+1][col]
                    t2.ox, t1.ox = t1.ox, t2.ox
                    t2.oy, t1.oy = t1.oy, t2.oy
                    self.board_array[i+1][col], self.board_array[i][col] = t1, t2
                    t1.iy = i+1
                    t2.iy = i
        elif dir == "up":
            for i in range(3):
                if self.board_array[i][col].number == 0 and self.board_array[i+1][col].number != 0:
                    t1 = self.board_array[i+1][col]
                    t2 = self.board_array[i][col]
                    t2.ox, t1.ox = t1.ox, t2.ox
                    t2.oy, t1.oy = t1.oy, t2.oy
                    self.board_array[i][col], self.board_array[i+1][col] = t1, t2
                    t1.iy = i
                    t2.iy = i+1

    def col_squash_same_numbers(self, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                t1 = self.board_array[i+1][col]
                t2 = self.board_array[i][col]
                if t1.number != 0 and t2.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.oy = i
                    t2.iy = i+1
                    self.score += t1.number
                    
        elif dir == "up":
            for i in range(3):
                t1 = self.board_array[i][col]
                t2 = self.board_array[i+1][col]
                if t1.number != 0 and t2.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.oy = i+1
                    t2.iy = i
                    self.score += t1.number

    def squash_col(self, x, dir="down"):
        for _ in range(3):
            self.col_squash_empty_spaces(x, dir)
        self.col_squash_same_numbers(x, dir)
        for _ in range(3):
            self.col_squash_empty_spaces(x, dir)

    def row_squash_empty_spaces(self, y, dir="right"):
        row = self.board_array[y]
        if dir == "right":
            for i in range(2, -1, -1):
                if row[i+1].number == 0 and row[i].number != 0:
                    t1 = row[i]
                    t2 = row[i+1]
                    t2.ox, t1.ox = t1.ox, t2.ox
                    t2.oy, t1.oy = t1.oy, t2.oy
                    row[i+1], row[i] = t1, t2
                    t1.ix, t1.iy = i+1, y
                    t2.ix, t2.iy = i, y
        elif dir == "left":
            for i in range(3):
                if row[i].number == 0 and row[i+1].number != 0:
                    t1 = row[i+1]
                    t2 = row[i]
                    t2.ox, t1.ox = t1.ox, t2.ox
                    t2.oy, t1.oy = t1.oy, t2.oy
                    row[i], row[i+1] = t1, t2
                    t1.ix, t1.iy = i, y
                    t2.ix, t2.iy = i+1, y

    def row_squash_same_numbers(self, y, dir="right"):
        row = self.board_array[y]
        if dir == "right":
            for i in range(2, -1, -1):
                t1 = row[i+1]
                t2 = row[i]
                if t1.number != 0 and t2.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.ox, t2.oy = i, y
                    t2.ix, t2.iy = i+1, y
                    self.score += t1.number
        elif dir == "left":
            for i in range(3):
                t1 = row[i]
                t2 = row[i+1]
                if t1.number != 0 and t2.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.ox, t2.oy = i+1, y
                    t2.ix, t2.iy = i, y
                    self.score += t1.number

    def squash_row(self, y, dir="right"):
        for _ in range(3):
            self.row_squash_empty_spaces(y, dir)
        self.row_squash_same_numbers(y, dir)
        for _ in range(3):
            self.row_squash_empty_spaces(y, dir)

    def execute_move(self, move_func):
        if self.curframe < self.max_frame:
            return  
            
        self.update_all_olds()
        move_func()
        self.spawn_number()
        self.curframe = 0

    def move_right(self):
        for y in range(4):
            self.squash_row(y, dir="right")

    def move_left(self):
        for y in range(4):
            self.squash_row(y, dir="left")

    def move_down(self):
        for x in range(4):
            self.squash_col(x, dir="down")

    def move_up(self):
        for x in range(4):
            self.squash_col(x, dir="up")

    def draw_stuff(self):
        bitmaptools.fill_region(self.canvas_bitmap, 0, 0, self.canvas_width, self.canvas_height, 0)
        
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                if tile.number == 0:
                    continue
                    
                tile_idx = self.val_to_palette_index(tile.number)
                px = x * self.scale
                py = y * self.scale
                
                bitmaptools.blit(
                    self.canvas_bitmap, 
                    self.tilesheet, 
                    px, py, 
                    x1=tile_idx * self.scale, 
                    y1=0, 
                    x2=(tile_idx + 1) * self.scale, 
                    y2=self.scale
                )
    
    def draw_text_direct(self, dest_bitmap, text, font, start_x, start_y, color_index=1):
        current_x = start_x
        font.load_glyphs(text)
        
        for char in text:
            glyph = font.get_glyph(ord(char))
            if not glyph:
                continue
            
            glyph_bitmap = glyph.bitmap
            width = glyph.width
            height = glyph.height
            dx = glyph.dx
            dy = glyph.dy
            
            offset_x = current_x + dx
            offset_y = start_y - dy - height
            
            for y in range(height):
                for x in range(width):
                    if glyph_bitmap[x, y]:
                        target_x = offset_x + x
                        target_y = offset_y + y
                        
                        if 0 <= target_x < dest_bitmap.width and 0 <= target_y < dest_bitmap.height:
                            dest_bitmap[target_x, target_y] = color_index
                            
            current_x += glyph.shift_x
                
    def setActiveArrow(self, i:int):
        for a in self.arrows:
            a.fill = 0x333333
        self.arrows[i].fill = 0xFFFFFF
            
    def game_short_next(self):
        self.direction_index = (self.direction_index - 1) % len(self.directions)
        self.setActiveArrow(self.direction_index)

    def game_short_select(self):
        d = self.directions[self.direction_index]
        if d == "left":
            self.execute_move(self.move_left)
        elif d == "right":
            self.execute_move(self.move_right)
        elif d == "up":
            self.execute_move(self.move_up)
        elif d == "down":
            self.execute_move(self.move_down)
        
    def game_update_frame(self):
        if self.curframe < self.max_frame:
            progress = self.curframe / float(self.max_frame)
            
            bitmaptools.fill_region(self.canvas_bitmap, 0, 0, self.canvas_width, self.canvas_height, 0)
            
            for y in range(4):
                for x in range(4):
                    tile = self.board_array[y][x]
                    if tile.number == 0:
                        continue
                        
                    tile_idx = self.val_to_palette_index(tile.number)
                    
                    start_px_x = tile.ox * self.scale
                    start_px_y = tile.oy * self.scale
                    target_px_x = tile.ix * self.scale
                    target_px_y = tile.iy * self.scale
                    
                    current_x = start_px_x + (target_px_x - start_px_x) * progress
                    current_y = start_px_y + (target_px_y - start_px_y) * progress
                    
                    bitmaptools.blit(
                        self.canvas_bitmap, 
                        self.tilesheet, 
                        int(current_x), int(current_y), 
                        x1=tile_idx * self.scale, 
                        y1=0, 
                        x2=(tile_idx + 1) * self.scale, 
                        y2=self.scale
                    )
            
            self.curframe += 1
            
            if self.curframe >= self.max_frame:
                for y in range(4):
                    for x in range(4):
                        tile = self.board_array[y][x]
                        tile.ix = x
                        tile.iy = y
                        tile.ox = x
                        tile.oy = y
                self.draw_stuff()