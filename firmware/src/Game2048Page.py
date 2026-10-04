import displayio
import random
from adafruit_display_text import label
from fonts import NINE_BOLD
from GamePage import GamePage
from adafruit_display_shapes.triangle import Triangle
import bitmaptools
from my_utilities import add_outline


class MemoryNumber:
    def __init__(self, number, x, y, tile_grid):
        self.number = number
        self.ix = x # cell where move ended (new)
        self.iy = y
        self.ox = x # cell where move started (old)
        self.oy = y
        self.into = None # cell this cell merged into (new) if any
        self.tile_grid = tile_grid

    def update_old(self):
        self.ox = self.ix
        self.oy = self.iy


TILESHEET = displayio.Bitmap(40 * 12, 40, 14)
_tilesheet_drawn = False

class Game2048Page(GamePage):
    def __init__(self, store):
        super().__init__(header="2048 Game", fps=100)

        self.width = 4
        self.height = 4
        self.store = store
        self.scale = 40

        boardx = 40
        boardy = 50
        self.boardx = boardx
        self.boardy = boardy

        # make this transparent
        add_outline(self.group,
            x=boardx - 1,
            y=boardy - 1,
            width=self.width * self.scale + 2,
            height=self.height * self.scale + 2,
            fill=0x111111,
            outline=0xFFFFFF
        )

        # ARROWS UI!!
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

        self.active_animations = []
        self.max_frame = 4
        self.curframe = 4

        # go gpt go:
        self.palette = displayio.Palette(14)
        self.palette[0] = 0x000000
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
        
        # make transparent (idk why this method exists)
        self.palette.make_transparent(0)

        num_tile_types = 12
        tilesheet_width = self.scale * num_tile_types
        tilesheet_height = self.scale
        # self.tilesheet = displayio.Bitmap(tilesheet_width, tilesheet_height, 14)

        # tile_values = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
        # for idx, val in enumerate(tile_values):
        #     x_offset = idx * self.scale
        #     color_idx = self.val_to_palette_index(val)
        #     bitmaptools.fill_region(self.tilesheet, x_offset, 0, x_offset + self.scale, self.scale, color_idx)

        #     if val != 0:
        #         text = str(val)
        #         text_color = 12 if val <= 4 else 13
        #         text_x = x_offset + 15
        #         text_y = 26
        #         self.draw_text_direct(self.tilesheet, text, NINE_BOLD, text_x, text_y, text_color)
        
        
        
        global _tilesheet_drawn
        self.tilesheet = TILESHEET
        if not _tilesheet_drawn:
            tile_values = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
            for idx, val in enumerate(tile_values):
                x_offset = idx * self.scale
                color_idx = self.val_to_palette_index(val)
                bitmaptools.fill_region(self.tilesheet, x_offset, 0, x_offset + self.scale, self.scale, color_idx)
                if val != 0:
                    text_color = 12 if val <= 4 else 13
                    self.draw_text_direct(self.tilesheet, str(val), NINE_BOLD, x_offset + 15, 26, text_color)
            _tilesheet_drawn = True

        self.board_group = displayio.Group(x=boardx, y=boardy)
        self.group.append(self.board_group)

        # add all the memory number into the board array!
        self.board_array = []
        for y in range(4):
            row = []
            for x in range(4):
                tile_grid = displayio.TileGrid(
                    self.tilesheet,
                    pixel_shader=self.palette,
                    width=1,
                    height=1,
                    tile_width=self.scale,
                    tile_height=self.scale,
                    x=x * self.scale,
                    y=y * self.scale
                )
                tile_grid[0] = 0
                self.board_group.append(tile_grid)
                row.append(MemoryNumber(0, x, y, tile_grid))
            self.board_array.append(row)

        self.score = 0
        self.spawn_new_numbers = [2, 4]
        self.directions = ["right", "up", "left", "down"]
        self.arrows = [self.arrowRight, self.arrowUp, self.arrowLeft, self.arrowDown]
        self.direction_index = 0
        self.setActiveArrow(self.direction_index)

        self.game_reset()

    def game_reset(self):
        self.curframe = self.max_frame
        self.active_animations = []
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                tile.number = 0
                tile.ix = x
                tile.iy = y
                tile.ox = x
                tile.oy = y
                tile.into = None
        self.score = 0
        self.spawn_number()
        self.spawn_number()
        self.sync_board_visuals()

    def spawn_number(self):
        empty_tiles = []
        for y in range(4):
            for x in range(4):
                if self.board_array[y][x].number == 0:
                    empty_tiles.append((x, y))
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
        else:
            return min(val.bit_length() - 1, 11)



    
    def update_all_olds(self):
        # before a move, update every tile's origin = the new postion it is in right now
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                tile.update_old()
                tile.ix = x
                tile.iy = y
                tile.ox = x
                tile.oy = y
                tile.into = None

    def sync_board_visuals(self):
        # snap every tile_grid to its real cell and real number by it's x and y position (bitmap)
        for y in range(4):
            for x in range(4):
                tile = self.board_array[y][x]
                tile.tile_grid[0] = self.val_to_palette_index(tile.number)
                tile.tile_grid.x = x * self.scale
                tile.tile_grid.y = y * self.scale



    # claude-edited:
    # ------------------------------------------------------------------
    # squashing. ox/oy are set once (update_all_olds) and never touched here.
    # ix/iy follow the tile objects as they swap places in board_array.
    # A merged-away tile just remembers who it merged into (.into); its own
    # ix/iy get pointed at that survivor's final cell after the move.
    # ------------------------------------------------------------------
    def col_squash_empty_spaces(self, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                if self.board_array[i+1][col].number == 0 and self.board_array[i][col].number != 0:
                    t1 = self.board_array[i][col]
                    t2 = self.board_array[i+1][col]
                    self.board_array[i+1][col], self.board_array[i][col] = t1, t2
                    t1.ix, t1.iy = col, i+1
                    t2.ix, t2.iy = col, i

        elif dir == "up":
            for i in range(3):
                if self.board_array[i][col].number == 0 and self.board_array[i+1][col].number != 0:
                    t1 = self.board_array[i+1][col]
                    t2 = self.board_array[i][col]
                    self.board_array[i][col], self.board_array[i+1][col] = t1, t2
                    t1.ix, t1.iy = col, i
                    t2.ix, t2.iy = col, i+1

    def now_move(self, move):
            # if processing last move, ignore
            if self.curframe < self.max_frame:
                return
    
            self.update_all_olds()   # origins = where everything is right now
            move()                   # squash: updates board_array, ix/iy, .into
    
            # merged-away tiles slide toward their survivor's final cell
            for y in range(4):
                for x in range(4):
                    tile = self.board_array[y][x]
                    if tile.into is not None:
                        tile.ix = tile.into.ix
                        tile.iy = tile.into.iy
    
            # every tile whose origin != destination animates, empty ones included
            # (they're invisible). tile_grid[0] is NOT touched here: each grid keeps
            # showing its old number until sync_board_visuals() at the end.
            anims = []
            for y in range(4):
                for x in range(4):
                    tile = self.board_array[y][x]
                    if tile.ox != tile.ix or tile.oy != tile.iy:
                        anims.append([
                            tile.tile_grid,
                            tile.ox * self.scale, tile.oy * self.scale,
                            tile.ix * self.scale, tile.iy * self.scale
                        ])
    
            # nothing moved or merged -> not a real move: no spawn, no animation
            if not anims:
                return
    
            self.active_animations = anims
            self.spawn_number()      # after anims are captured; it rewrites ix/iy/ox/oy
            self.curframe = 0





    def col_squash_same_numbers(self, col, dir="down"):
        if dir == "down":
            for i in range(2, -1, -1):
                t1 = self.board_array[i+1][col]
                t2 = self.board_array[i][col]
                if t1.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.into = t1
                    self.score += t1.number

        elif dir == "up":
            for i in range(3):
                t1 = self.board_array[i][col]
                t2 = self.board_array[i+1][col]
                if t1.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.into = t1
                    self.score += t1.number

    def squash_col(self, x, dir="down"):
        for _ in range(3):
            self.col_squash_empty_spaces(x, dir)
        self.col_squash_same_numbers(x, dir)
        self.col_squash_empty_spaces(x, dir)

    def row_squash_empty_spaces(self, y, dir="right"):
        row = self.board_array[y]
        if dir == "right":
            for i in range(2, -1, -1):
                if row[i+1].number == 0 and row[i].number != 0:
                    t1 = row[i]
                    t2 = row[i+1]
                    row[i+1], row[i] = t1, t2
                    t1.ix, t1.iy = i+1, y
                    t2.ix, t2.iy = i, y
        elif dir == "left":
            for i in range(3):
                if row[i].number == 0 and row[i+1].number != 0:
                    t1 = row[i+1]
                    t2 = row[i]
                    row[i], row[i+1] = t1, t2
                    t1.ix, t1.iy = i, y
                    t2.ix, t2.iy = i+1, y

    def row_squash_same_numbers(self, y, dir="right"):
        row = self.board_array[y]
        if dir == "right":
            for i in range(2, -1, -1):
                t1 = row[i+1]
                t2 = row[i]
                if t1.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.into = t1
                    self.score += t1.number
        elif dir == "left":
            for i in range(3):
                t1 = row[i]
                t2 = row[i+1]
                if t1.number != 0 and t1.number == t2.number:
                    t1.number *= 2
                    t2.number = 0
                    t2.into = t1
                    self.score += t1.number

    def squash_row(self, y, dir="right"):
        for _ in range(3):
            self.row_squash_empty_spaces(y, dir)
        self.row_squash_same_numbers(y, dir)
        self.row_squash_empty_spaces(y, dir)

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

    def setActiveArrow(self, i: int):
        for a in self.arrows:
            a.fill = 0x333333
        self.arrows[i].fill = 0xFFFFFF

    def game_short_next(self):
        self.direction_index = (self.direction_index - 1) % len(self.directions)
        self.setActiveArrow(self.direction_index)

    def game_short_select(self):
        d = self.directions[self.direction_index]
        if d == "left":
            self.now_move(self.move_left)
        elif d == "right":
            self.now_move(self.move_right)
        elif d == "up":
            self.now_move(self.move_up)
        elif d == "down":
            self.now_move(self.move_down)

    # larp
    def game_update_frame(self):
        if self.curframe < self.max_frame:
            # 1/10 ... 10/10, the last larp frame lands 1/1 on target
            larp = (self.curframe + 1) / float(self.max_frame)

            for anim in self.active_animations:
                tile_grid, sx, sy, tx, ty = anim
                tile_grid.x = int(sx + (tx - sx) * larp)
                tile_grid.y = int(sy + (ty - sy) * larp)

            self.curframe += 1

            # the larp ends
            if self.curframe >= self.max_frame:
                self.active_animations = []

                # reset the stuff
                for y in range(4):
                    for x in range(4):
                        tile = self.board_array[y][x]
                        tile.ix = x
                        tile.iy = y
                        tile.ox = x
                        tile.oy = y
                        tile.into = None

                # ghost should go back to its original block to be reused?
                self.sync_board_visuals()