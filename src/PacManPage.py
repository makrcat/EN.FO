import random
import time
import displayio

from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_text import label
import terminalio
from my_utilities import add_outline

from GamePage import GamePage


class PacManGame:
    def __init__(self, boardx, boardy, scale=10):
        self.group = displayio.Group(x=boardx, y=boardy)

        self.width = 19
        self.height = 21
        self.scale = scale
        self.score = 0

        self.directions = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
        ]

        self.bitmap = displayio.Bitmap(
            scale, scale * 4, 4
        )
        self.palette = displayio.Palette(4)
        self.palette[0] = 0x000000
        self.palette[1] = 0x0000FF
        self.palette[2] = 0xFFB8FF
        self.palette[3] = 0xFFFFFF

        # sprite for tile 1
        for y in range(scale):
            for x in range(scale):
                self.bitmap[x, scale * 1 + y] = 1

        for y in range(4, 6):
            for x in range(4, 6):
                self.bitmap[x, scale * 2 + y] = 2

        for y in range(3, 7):
            for x in range(3, 7):
                self.bitmap[x, scale * 3 + y] = 3

        self.tile_grid = displayio.TileGrid(
            self.bitmap,
            pixel_shader=self.palette,
            width=self.width,
            height=self.height,
            tile_width=scale,
            tile_height=scale,
        )
        self.group.append(self.tile_grid)

        radius = scale // 2 - 1

        self.pacman_shape = Circle(
            x0=0, y0=0, r=radius, fill=0xFFFF00
        )
        self.ghost_shape = Rect(
            x=0, y=0, width=scale, height=scale,
            fill=0xFF00FF
        )

        self.mouthUp_group = displayio.Group()
        self.mouthUp_group.append(
            Triangle(0, 0, -3, -radius, 3, -radius, fill=0x000000)
        )

        self.mouthDown_group = displayio.Group()
        self.mouthDown_group.append(
            Triangle(0, 0, -3, radius, 3, radius, fill=0x000000)
        )

        self.mouthLeft_group = displayio.Group()
        self.mouthLeft_group.append(
            Triangle(0, 0, -radius, -3, -radius, 3, fill=0x000000)
        )

        self.mouthRight_group = displayio.Group()
        self.mouthRight_group.append(
            Triangle(0, 0, radius, -3, radius, 3, fill=0x000000)
        )

        arrow_offset = radius + 4

        self.arrowUp_group = displayio.Group()
        self.arrowUp_group.append(
            Triangle(
                0, -arrow_offset - 3,
                -3, -arrow_offset,
                3, -arrow_offset,
                fill=0xFFFFFF,
            )
        )

        self.arrowDown_group = displayio.Group()
        self.arrowDown_group.append(
            Triangle(
                0, arrow_offset + 3,
                -3, arrow_offset,
                3, arrow_offset,
                fill=0xFFFFFF,
            )
        )

        self.arrowLeft_group = displayio.Group()
        self.arrowLeft_group.append(
            Triangle(
                -arrow_offset - 3, 0,
                -arrow_offset, -3,
                -arrow_offset, 3,
                fill=0xFFFFFF,
            )
        )

        self.arrowRight_group = displayio.Group()
        self.arrowRight_group.append(
            Triangle(
                arrow_offset + 3, 0,
                arrow_offset, -3,
                arrow_offset, 3,
                fill=0xFFFFFF,
            )
        )

        self.sprites_group = displayio.Group()

        for sprite in (
            self.pacman_shape,
            self.ghost_shape,
            self.mouthUp_group,
            self.mouthDown_group,
            self.mouthLeft_group,
            self.mouthRight_group,
            self.arrowUp_group,
            self.arrowDown_group,
            self.arrowLeft_group,
            self.arrowRight_group,
        ):
            self.sprites_group.append(sprite)

        self.group.append(self.sprites_group)

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
        self.pacman_move_dir = 1
        self.pacman_input_dir = 1

        self.ghost_pos = [9, 9]
        self.ghost_dir = 0

        self.score = 0
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

        dx, dy = self.directions[self.pacman_input_dir]
        test_x = self.pacman_pos[0] + dx

        if test_x < 0:
            test_x = self.width - 1
        elif test_x >= self.width:
            test_x = 0

        if not self.is_wall(test_x, self.pacman_pos[1] + dy):
            self.pacman_move_dir = self.pacman_input_dir

        dx, dy = self.directions[self.pacman_move_dir]
        next_x = self.pacman_pos[0] + dx
        next_y = self.pacman_pos[1] + dy

        if next_x < 0:
            next_x = self.width - 1
        elif next_x >= self.width:
            next_x = 0

        if not self.is_wall(next_x, next_y):
            self.pacman_pos = [next_x, next_y]

            current_tile = self.tile_grid[next_x, next_y]

            if current_tile == 2 or current_tile == 3:
                self.tile_grid[next_x, next_y] = 0

            if current_tile == 2:
                self.score += 1
            elif current_tile == 3:
                self.score += 5

        valid_dirs = []

        for i, (dx, dy) in enumerate(self.directions):
            if i == (self.ghost_dir + 2) % 4:
                continue

            test_x = self.ghost_pos[0] + dx

            if test_x < 0:
                test_x = self.width - 1
            elif test_x >= self.width:
                test_x = 0

            if not self.is_wall(
                test_x,
                self.ghost_pos[1] + dy,
            ):
                valid_dirs.append(i)

        if not valid_dirs:
            valid_dirs.append((self.ghost_dir + 2) % 4)

        if (
            self.ghost_dir not in valid_dirs
            or random.random() < 0.3
        ):
            self.ghost_dir = random.choice(valid_dirs)

        dx, dy = self.directions[self.ghost_dir]

        next_x = self.ghost_pos[0] + dx
        next_y = self.ghost_pos[1] + dy

        if next_x < 0:
            next_x = self.width - 1
        elif next_x >= self.width:
            next_x = 0

        self.ghost_pos = [next_x, next_y]

        if self.pacman_pos == self.ghost_pos:
            self.is_dead = True
            self.dead_time = time.monotonic()

    def draw_stuff(self):
        half = self.scale // 2

        pac_x = self.pacman_pos[0] * self.scale + half
        pac_y = self.pacman_pos[1] * self.scale + half

        self.pacman_shape.x0 = pac_x
        self.pacman_shape.y0 = pac_y

        self.ghost_shape.x = self.ghost_pos[0] * self.scale
        self.ghost_shape.y = self.ghost_pos[1] * self.scale

        mouths = [
            self.mouthUp_group,
            self.mouthRight_group,
            self.mouthDown_group,
            self.mouthLeft_group,
        ]

        arrows = [
            self.arrowUp_group,
            self.arrowRight_group,
            self.arrowDown_group,
            self.arrowLeft_group,
        ]

        for i, group in enumerate(mouths):
            group.x = pac_x
            group.y = pac_y
            group.hidden = i != self.pacman_move_dir

        for i, group in enumerate(arrows):
            group.x = pac_x
            group.y = pac_y
            group.hidden = i != self.pacman_input_dir

        self.sprites_group.hidden = self.is_dead

    def update(self):
        self.game_step()
        self.draw_stuff()

    def rotate_next(self):
        self.pacman_input_dir = (self.pacman_input_dir + 1) % 4

    def rotate_prev(self):
        self.pacman_input_dir = (self.pacman_input_dir - 1) % 4

class PacManPage(GamePage):
    def __init__(self, store):
        super().__init__(
            header="Circuit Pac-Man",
            fps=8,
        )

        self.store = store

        boardx = 25
        boardy = 28
        scale = 10

        self.boardx = boardx
        self.boardy = boardy

        add_outline(self.group,
            x=boardx - 1,
            y=boardy - 1,
            width=19 * scale + 2,
            height=21 * scale + 2,
            fill=None,
            outline=0xFFFFFF,
        )

        self.game = PacManGame(
            boardx=boardx,
            boardy=boardy,
            scale=scale,
        )
        self.group.append(self.game.group)

        max_score_text = "score: 9999"

        self.score_bg = Rect(
            x=22,
            y=20,
            width=len(max_score_text) * 6 + 4,
            height=11,
            fill=0xFFFFFF,
        )
        self.group.append(self.score_bg)

        self.scoreLabel = label.Label(
            terminalio.FONT,
            text="score: 0",
            color=0x000000,
            anchor_point=(0.0, 0.0),
            anchored_position=(25, 20),
            scale=1,
        )
        self.group.append(self.scoreLabel)

    def game_update_frame(self):
        self.game.update()
        self.scoreLabel.text = f"score: {self.game.score}"

    def game_short_next(self):
        self.game.rotate_next()

    def game_short_select(self):
        self.game.rotate_prev()