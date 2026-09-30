import displayio
import random
from adafruit_display_text import label
from fonts import NINE_BOLD
from GamePage import GamePage
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
import time, bitmaptools

class Game2048Page(GamePage):
    def __init__(self, store):
        super().__init__(header="2048 Game", fps=10)
        
        self.width = 4
        self.height = 4
        self.store = store
        self.scale = 40  # Size of each tile in pixels
        
        boardx = 40
        boardy = 50
        self.boardx = boardx
        self.boardy = boardy
    
        # --- outline ---
        self.outline = Rect(
            x=boardx - 1, 
            y=boardy - 1, 
            width=self.width * self.scale + 2, 
            height=self.height * self.scale + 2,
            fill=None, 
            outline=0xFFFFFF
        )
        self.group.append(self.outline)
        
        # --- arrows (unchanged) ---
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
        
        
        
        self.palette[0] = 0x111111  # 
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
        self.palette[12] = 0x111111 # light tiles
        self.palette[13] = 0xFFFFFF # 8 + tiles

        # --- tilesheet bitmap ---
        num_tile_types = 12
        tilesheet_width = self.scale * num_tile_types
        tilesheet_height = self.scale
        self.tilesheet = displayio.Bitmap(tilesheet_width, tilesheet_height, 14)
        
        # all possible tile graphics
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

        # --- tilegrid array ---
        self.board_group = displayio.Group(x=boardx, y=boardy)
        self.tile_grids = [[None for _ in range(4)] for _ in range(4)]
        
        for y in range(4):
            for x in range(4):

                tg = displayio.TileGrid(
                    self.tilesheet, 
                    pixel_shader=self.palette,
                    width=1, 
                    height=1,
                    tile_width=self.scale,
                    tile_height=self.scale
                )
                tg.x = x * self.scale
                tg.y = y * self.scale
                tg[0, 0] = 0
                self.tile_grids[y][x] = tg
                self.board_group.append(tg)

        self.group.append(self.board_group)

        self.board_array = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.spawn_new_numbers = [2, 4]
        self.directions = ["right", "up", "left", "down"]
        self.arrows = [self.arrowRight, self.arrowUp, self.arrowLeft, self.arrowDown]
        self.direction_index = 0
        self.setActiveArrow(self.direction_index)
        
        self.game_reset()
        self.draw_stuff()

    def game_reset(self):
        self.board_array = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.spawn_number()
        self.spawn_number()
        
    def spawn_number(self):
        empty_tiles = [(x, y) for y in range(4) for x in range(4) if self.board_array[y][x] == 0]
        if empty_tiles:
            rx, ry = random.choice(empty_tiles)
            self.board_array[ry][rx] = random.choice(self.spawn_new_numbers)

    def val_to_palette_index(self, val):
        if val == 0:
            return 0
        index = 0
        while val > 1:
            val //= 2
            index += 1
        return min(index, 11)

    # --- movement ---
    def col_squash_empty_spaces(self, board, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                if board[i+1][col] == 0:
                    board[i][col], board[i+1][col] = board[i+1][col], board[i][col]
        elif dir == "up":
            for i in range(3):
                if board[i][col] == 0:
                    board[i][col], board[i+1][col] = board[i+1][col], board[i][col]

    def col_squash_same_numbers(self, board, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                if board[i+1][col] == board[i][col] and board[i][col] != 0:
                    board[i+1][col] *= 2
                    board[i][col] = 0
                    self.score += board[i+1][col]
        elif dir == "up":
            for i in range(3):
                if board[i][col] == board[i+1][col] and board[i+1][col] != 0:
                    board[i][col] *= 2
                    board[i+1][col] = 0
                    self.score += board[i][col]

    def squash_col(self, col, dir="down"):
        for _ in range(3):
            self.col_squash_empty_spaces(self.board_array, col, dir)
        self.col_squash_same_numbers(self.board_array, col, dir)
        for _ in range(3):
            self.col_squash_empty_spaces(self.board_array, col, dir)

    def row_squash_empty_spaces(self, row, dir="right"):
        if dir == "right":
            for i in range(3):
                if row[i+1] == 0:
                    row[i+1], row[i] = row[i], row[i+1]
        elif dir == "left":
            for i in range(3, 0, -1):
                if row[i - 1] == 0:
                    row[i-1], row[i] = row[i], row[i-1]

    def row_squash_same_numbers(self, row, dir="right"):
        if dir == "right":
            for i in range(2, -1, -1):
                if row[i+1] == row[i] and row[i] != 0:
                    row[i+1] *= 2
                    row[i] = 0
                    self.score += row[i+1]
        elif dir == "left":
            for i in range(3):
                if row[i] == row[i+1] and row[i+1] != 0:
                    row[i] *= 2
                    row[i+1] = 0
                    self.score += row[i]

    def squash_row(self, row, dir="right"):
        for _ in range(3):
            self.row_squash_empty_spaces(row, dir)
        self.row_squash_same_numbers(row, dir)
        self.row_squash_empty_spaces(row, dir)

    def move_right(self):
        for row in self.board_array:
            self.squash_row(row, dir="right")
        self.spawn_number()

    def move_left(self):
        for row in self.board_array:
            self.squash_row(row, dir="left")
        self.spawn_number()

    def move_down(self):
        for i in range(4):
            self.squash_col(i, dir="down")
        self.spawn_number()

    def move_up(self):
        for i in range(4):
            self.squash_col(i, dir="up")
        self.spawn_number()
        





    def draw_stuff(self):
        for y in range(4):
            for x in range(4):
                val = self.board_array[y][x]
                tile_idx = self.val_to_palette_index(val)

                # point to the right graphic
                self.tile_grids[y][x][0, 0] = tile_idx
    
    def draw_text_direct(self, dest_bitmap, text, font, start_x, start_y, color_index=1):
        """Blits characters directly into a target bitmap to save RAM."""
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
            a.fill = 0x444444
        self.arrows[i].fill = 0xFFFFFF
            
    def game_short_next(self):
        self.direction_index = (self.direction_index - 1) % len(self.directions)
        self.setActiveArrow(self.direction_index)

    def game_short_select(self):
        d = self.directions[self.direction_index]
        if d == "left":
            self.move_left()
        elif d == "right":
            self.move_right()
        elif d == "up":
            self.move_up()
        elif d == "down":
            self.move_down()
        else:
            print("what")
        
    def game_update_frame(self):
        self.draw_stuff()