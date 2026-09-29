import displayio
import random
from adafruit_display_text import label
from fonts import NINE
from GamePage import GamePage
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.triangle import Triangle
import time

class PacManPage(GamePage):
    def __init__(self, store):
        super().__init__(header="Circuit Pac-Man", fps=8)
        
        self.width = 19
        self.height = 21
        self.scale = 10
        self.store = store
        
        boardx = 20
        boardy = 30
        self.boardx = boardx
        self.boardy = boardy
    
        self.outline = Rect(
            x=boardx-1, 
            y=boardy-1, 
            width = self.width * self.scale + 2, 
            height = self.height * self.scale + 2,
            fill = None, 
            outline=0x0000FF # blue arcade walls
        )
        self.group.append(self.outline)
        
        # sprite sheet bitmap
        self.bitmap = displayio.Bitmap(self.scale, self.scale * 4, 4)

        self.palette = displayio.Palette(4)
        self.palette[0] = 0x000000 # black
        self.palette[1] = 0x0000FF # blue
        self.palette[2] = 0xFFB8FF # pink
        self.palette[3] = 0xFFFFFF # white

        
        for y in range(self.scale):
            for x in range(self.scale):
                self.bitmap[x, 10 + y] = 1

        for y in range(4, 6):
            for x in range(4, 6):
                self.bitmap[x, 20 + y] = 2

        for y in range(3, 7):
            for x in range(3, 7):
                self.bitmap[x, 30 + y] = 3

        self.tile_grid = displayio.TileGrid(
            self.bitmap, 
            pixel_shader=self.palette,
            width=self.width,
            height=self.height,
            tile_width=self.scale,
            tile_height=self.scale
        )
        
        self.board_group = displayio.Group(x=boardx, y=boardy)
        self.board_group.append(self.tile_grid)
        self.group.append(self.board_group)

        radius = self.scale // 2
        self.pacman_shape = Circle(x0=0, y0=0, r=radius, fill=0xFFFF00)
        
        # ghost (red)
        self.ghost_shape = Rect(x=0, y=0, width=self.scale, height=self.scale, fill=0xFF0000)
        
        # center triangles, inward
        self.arrowUp_group = displayio.Group()
        self.arrowUp_group.append(Triangle(0, 0, -3, -radius, 3, -radius, fill=0x000000))

        self.arrowDown_group = displayio.Group()
        self.arrowDown_group.append(Triangle(0, 0, -3, radius, 3, radius, fill=0x000000))

        self.arrowLeft_group = displayio.Group()
        self.arrowLeft_group.append(Triangle(0, 0, -radius, -3, -radius, 3, fill=0x000000))

        self.arrowRight_group = displayio.Group()
        self.arrowRight_group.append(Triangle(0, 0, radius, -3, radius, 3, fill=0x000000))

        # main sprites
        self.sprites_group = displayio.Group(x=boardx, y=boardy)
        self.sprites_group.append(self.pacman_shape)
        self.sprites_group.append(self.ghost_shape)
        
        self.sprites_group.append(self.arrowUp_group)
        self.sprites_group.append(self.arrowDown_group)
        self.sprites_group.append(self.arrowLeft_group)
        self.sprites_group.append(self.arrowRight_group)
        
        self.group.append(self.sprites_group)
        
        # UP, RIGHT, DOWN, LEFT
        self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        self.game_reset()
        
    def game_reset(self):
        raw_maze = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
            [1,3,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,3,1],
            [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1],
            [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
            [1,1,1,1,2,1,1,1,0,1,0,1,1,1,2,1,1,1,1],
            [0,0,0,1,2,1,0,0,0,0,0,0,0,1,2,1,0,0,0],
            [1,1,1,1,2,1,0,1,1,0,1,1,0,1,2,1,1,1,1],
            [0,0,0,0,2,0,0,1,0,0,0,1,0,0,2,0,0,0,0],
            [1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1],
            [0,0,0,1,2,1,0,0,0,0,0,0,0,1,2,1,0,0,0],
            [1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1],
            [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
            [1,3,2,1,2,2,2,2,2,0,2,2,2,2,2,1,2,3,1],
            [1,1,2,1,2,1,2,1,1,1,1,1,2,1,2,1,2,1,1],
            [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
            [1,2,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
        
        for y in range(self.height):
            for x in range(self.width):
                self.tile_grid[x, y] = raw_maze[y][x]
                
        self.pacman_pos = [9, 14]
        self.pacman_dir = 1 # Start facing Right
        
        self.ghost_pos = [9, 9]
        self.ghost_dir = 0
        
        self.is_dead = False
        self.dead_time = 0
        
        self.draw_stuff()

    def is_wall(self, x, y):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return True
        return self.tile_grid[x, y] == 1

    def game_step(self):
        if self.is_dead:
            if time.monotonic() - self.dead_time > 1.5:
                self.game_reset()
            return
        
        cur_dx, cur_dy = self.directions[self.pacman_dir]
        next_x = self.pacman_pos[0] + cur_dx
        next_y = self.pacman_pos[1] + cur_dy

        if not self.is_wall(next_x, next_y):
            self.pacman_pos[0] = next_x
            self.pacman_pos[1] = next_y
            
            curent_tile = self.tile_grid[next_x, next_y]
            if curent_tile == 2 or curent_tile == 3:
                self.tile_grid[next_x, next_y] = 0
        else:
            # hit a wall: stop moving until turn
            pass

        valid_ghost_dirs = []
        for i, (tdx, tdy) in enumerate(self.directions):
            if i == (self.ghost_dir + 2) % 4:
                continue
            
            test_x = self.ghost_pos[0] + tdx
            if test_x < 0:
                test_x = self.width - 1
            elif test_x >= self.width:
                test_x = 0
                
            if not self.is_wall(test_x, self.ghost_pos[1] + tdy):
                valid_ghost_dirs.append(i)
                
        if not valid_ghost_dirs:
            valid_ghost_dirs.append((self.ghost_dir + 2) % 4)
            
        if self.ghost_dir not in valid_ghost_dirs or random.random() < 0.3:
            self.ghost_dir = random.choice(valid_ghost_dirs)
            
        gdx, gdy = self.directions[self.ghost_dir]
        next_gx = self.ghost_pos[0] + gdx
        next_gy = self.ghost_pos[1] + gdy

        if next_gx < 0:
            next_gx = self.width - 1
        elif next_gx >= self.width:
            next_gx = 0

        self.ghost_pos[0] = next_gx
        self.ghost_pos[1] = next_gy
        
        
        
        
        

        if self.pacman_pos[0] == self.ghost_pos[0] and self.pacman_pos[1] == self.ghost_pos[1]:
            self.is_dead = True
            self.dead_time = time.monotonic()

    def draw_stuff(self):
        half_scale = self.scale // 2
        
        pac_x = self.pacman_pos[0] * self.scale + half_scale
        pac_y = self.pacman_pos[1] * self.scale + half_scale
        
        self.pacman_shape.x0 = pac_x
        self.pacman_shape.y0 = pac_y
        
        self.ghost_shape.x = self.ghost_pos[0] * self.scale
        self.ghost_shape.y = self.ghost_pos[1] * self.scale
    
        for i, group in enumerate([self.arrowUp_group, self.arrowRight_group, self.arrowDown_group, self.arrowLeft_group]):
            group.x = pac_x
            group.y = pac_y
            group.hidden = (i != self.pacman_dir)
        
        self.sprites_group.hidden = self.is_dead

    def game_short_next(self):
            new_dir = (self.pacman_dir + 1) % 4
            dx, dy = self.directions[new_dir]
            
            if not self.is_wall(self.pacman_pos[0] + dx, self.pacman_pos[1] + dy):
                self.pacman_dir = new_dir
        
    def game_short_select(self):
        new_dir = (self.pacman_dir - 1) % 4
        dx, dy = self.directions[new_dir]
        
        if not self.is_wall(self.pacman_pos[0] + dx, self.pacman_pos[1] + dy):
            self.pacman_dir = new_dir
        
    def game_update_frame(self):
        self.game_step()
        self.draw_stuff()