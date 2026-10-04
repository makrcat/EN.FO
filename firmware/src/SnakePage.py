import displayio
import random
from adafruit_display_text import label
from fonts import NINE
from GamePage import GamePage
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
import random
import time
from my_utilities import add_outline

class SnakePage(GamePage):
    def __init__(self, store):
        super().__init__(header="Snake Game", fps=10)
        
        self.width = 20
        self.height = 20
        self.store = store
        self.scale = 10
        
        boardx = 20
        boardy = 30
        self.boardx = boardx
        self.boardy = boardy
    
        add_outline(self.group,
            x=boardx-1, 
            y=boardy-1, 
            width = self.width * self.scale + 2, 
            height = self.height * self.scale + 2,
            fill = None, 
            outline=0xFFFFFF)
        
        self.bitmap = displayio.Bitmap(self.width, self.height, 4)

        self.palette = displayio.Palette(4)
        self.palette[0] = 0x000000
        self.palette[1] = 0x00FF00
        self.palette[2] = 0xFF0000
        self.palette[3] = 0x999999

        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        
        
        self.board_group = displayio.Group(x=boardx, y=boardy, scale=self.scale)
        self.board_group.append(self.tile_grid)
        self.group.append(self.board_group)

        self.head_bitmap = displayio.OnDiskBitmap("graphics/snake_head.bmp")
        self.head_tile_grid = displayio.TileGrid(
            self.head_bitmap, 
            pixel_shader=self.head_bitmap.pixel_shader,
            tile_width=self.scale,
            tile_height=self.scale
        )
        
        # Load dead head
        self.dead_bitmap = displayio.OnDiskBitmap("graphics/snake_dead.bmp")
        self.dead_tile_grid = displayio.TileGrid(
            self.dead_bitmap, 
            pixel_shader=self.dead_bitmap.pixel_shader,
            tile_width=self.scale,
            tile_height=self.scale
        )
        
        self.head_group = displayio.Group()
        self.head_group.append(self.head_tile_grid)
        self.head_group.append(self.dead_tile_grid)
        self.group.append(self.head_group)
        
        # Start with dead grid hidden
        self.dead_tile_grid.hidden = True
        
        self.snake = [(2, 10), (1, 10), (0, 10)]
        self.snake_dead = False
        self.apple = (10, 10)
        self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] # clockwise
        self.d_index = 1
        
        self.head_orientations = [
            (True,  False, False), # 0: UP    (Swap axes)
            (False, False, False), # 1: RIGHT (Default)
            (True,  False, True),  # 2: DOWN  (Swap axes, flip vertical)
            (False, True,  False)  # 3: LEFT  (Flip horizontal)
        ]
        
        self.dead_time = 0
        
        self.draw_stuff()
    
    def game_reset(self):   
        self.snake = [(2, 10), (1, 10), (0, 10)]
        self.d_index = 1
        self.spawn_apple()
        
    def spawn_apple(self):
        all_coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        ava = [pos for pos in all_coords if pos not in self.snake]

        if ava:
            self.apple = random.choice(ava)
        
    def checkIfReviveYet(self):
        if not self.snake_dead:
            return True

        if time.monotonic() - self.dead_time > 1:
            self.snake_dead = False
            self.game_reset()
            return True

        return False

    def game_step(self):
        if not self.checkIfReviveYet():
            return

        old_x = self.snake[0][0]
        old_y = self.snake[0][1]

        dx = self.directions[self.d_index][0]
        dy = self.directions[self.d_index][1]

        new_one = (old_x + dx, old_y + dy)

        # Check if we're eating the apple
        hit_apple = new_one == self.apple

        # Check walls
        hit_wall = (
            new_one[0] < 0 or
            new_one[0] >= self.width or
            new_one[1] < 0 or
            new_one[1] >= self.height
        )

        if hit_wall:
            self.snake_dead = True
            self.dead_time = time.monotonic()
            return

        self.snake.insert(0, new_one)
        if not hit_apple:
            self.snake.pop()

        else:
            self.spawn_apple()

            if not self.checkIfReviveYet():
                return
            
            old_x = self.snake[0][0]
            old_y = self.snake[0][1]
            dx = self.directions[self.d_index][0]
            dy = self.directions[self.d_index][1]
            
            new_one = (old_x + dx, old_y + dy)
            
            hit_apple = False
            if new_one[0] == self.apple[0] and new_one[1] == self.apple[1]:
                self.spawn_apple()
                hit_apple = True
                
            hit_itself = new_one in self.snake
            
            if (new_one[0] < 0 or new_one[0] >= self.width or new_one[1] < 0 or new_one[1] >= self.height) or hit_itself:
                self.snake_dead = True
                self.dead_time = time.monotonic()
            else:
                self.snake.insert(0, new_one)
                if not hit_apple: self.snake.pop()  

    def draw_stuff(self):
        self.bitmap.fill(0)
        
        for i, segment in enumerate(self.snake):
            if 0 <= segment[0] < self.width and 0 <= segment[1] < self.height:
                if i == 0:
                    
                    
                    # select head tile grid
                    active_grid = self.dead_tile_grid if self.snake_dead else self.head_tile_grid
                    inactive_grid = self.head_tile_grid if self.snake_dead else self.dead_tile_grid
                    
                    active_grid.hidden = False
                    inactive_grid.hidden = True
                    
                   
                   
                   
                    active_grid.x = self.boardx + segment[0] * self.scale
                    active_grid.y = self.boardy + segment[1] * self.scale
                    
                    trans, fx, fy = self.head_orientations[self.d_index]
                    active_grid.transpose_xy = trans
                    active_grid.flip_x = fx
                    active_grid.flip_y = fy
                    
                else:
                    if self.snake_dead:
                        self.bitmap[segment[0], segment[1]] = 3
                    else:
                        self.bitmap[segment[0], segment[1]] = 1
                    
        if self.snake_dead and self.head_tile_grid:
            self.head_tile_grid.hidden = True
                
        self.bitmap[self.apple[0], self.apple[1]] = 2
            
    def game_short_next(self):
        if not self.snake_dead:
            self.d_index = (self.d_index + 1) % len(self.directions)
        
    def game_short_select(self):
        if not self.snake_dead:
            self.d_index = (self.d_index - 1) % len(self.directions)
        
    def game_update_frame(self):
        self.game_step()
        self.draw_stuff()