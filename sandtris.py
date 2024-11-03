import pygame
import pymunk
import random
import sys


pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sandtris")
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, -1000)  
space.iterations = 30
space.sleep_time_threshold = 0.5
space.collision_slop = 0.5


BLOCK_SIZE = 20
SAND_RADIUS = 2
FPS = 60

COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
    (0, 255, 255),  # Cyan
]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

tetromino_shapes = {
    'I': [(-2, 0), (-1, 0), (0, 0), (1, 0)],
    'O': [(-1, 0), (0, 0), (-1, 1), (0, 1)],
    'T': [(-1, 0), (0, 0), (1, 0), (0, 1)],
    'S': [(0, 0), (1, 0), (-1, 1), (0, 1)],
    'Z': [(-1, 0), (0, 0), (0, 1), (1, 1)],
    'J': [(-1, 0), (-1, 1), (0, 0), (1, 0)],
    'L': [(-1, 0), (0, 0), (1, 0), (1, 1)],
}

# Grid parameters for line detection
GRID_CELL_SIZE = SAND_RADIUS * 2
GRID_WIDTH = SCREEN_WIDTH // GRID_CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_CELL_SIZE
sand_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Create static floor
def create_static_floor():
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (0, 0), (SCREEN_WIDTH, 0), 1)
    shape.friction = 1.0
    space.add(body, shape)

# Tetromino class
class Tetromino:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.color = random.choice(COLORS)
        self.blocks = []
        self.create_blocks()

    def create_blocks(self):
        offsets = tetromino_shapes[self.shape_name]
        initial_y = SCREEN_HEIGHT - BLOCK_SIZE * 2  # Start near the top
        for offset in offsets:
            x = SCREEN_WIDTH // 2 + offset[0] * BLOCK_SIZE
            y = initial_y + offset[1] * BLOCK_SIZE
            block = create_block(x, y, self.color)
            self.blocks.append(block)

    def move(self, dx, dy):
        for block in self.blocks:
            block.body.position += (dx * BLOCK_SIZE, dy * BLOCK_SIZE)

    def rotate(self):
        pivot = self.blocks[0].body.position
        for block in self.blocks[1:]:
            rel = block.body.position - pivot
            new_rel = pymunk.Vec2d(-rel.y, rel.x)
            block.body.position = pivot + new_rel

    def check_collision(self):
        for block in self.blocks:
            if block.body.position.y - BLOCK_SIZE / 2 <= 0 or \
               block.body.position.x - BLOCK_SIZE / 2 < 0 or \
               block.body.position.x + BLOCK_SIZE / 2 > SCREEN_WIDTH:
                return True
            for shape in space.shapes:
                if shape not in [b.shape for b in self.blocks]:
                    if block.shape.shapes_collide(shape).points:
                        return True
        return False

    def land(self):
        for block in self.blocks:
            x, y = block.body.position
            space.remove(block.body, block.shape)
            mass = 1.0
            moment = pymunk.moment_for_box(mass, (BLOCK_SIZE, BLOCK_SIZE))
            block.body = pymunk.Body(mass, moment)
            block.body.position = x, y
            block.shape = pymunk.Poly.create_box(block.body, size=(BLOCK_SIZE, BLOCK_SIZE))
            block.shape.friction = 0.5
            block.shape.elasticity = 0
            block.shape.block = block
            space.add(block.body, block.shape)
            block.landed = True

# Block class
class Block:
    def __init__(self, x, y, color):
        self.color = color
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = x, y
        self.shape = pymunk.Poly.create_box(self.body, size=(BLOCK_SIZE, BLOCK_SIZE))
        self.shape.friction = 0.5
        self.shape.elasticity = 0
        self.shape.block = self  
        space.add(self.body, self.shape)
        self.landed = False

def create_block(x, y, color):
    return Block(x, y, color)

# Sand grains
class SandGrain:
    def __init__(self, x, y, color):
        mass = 0.1
        radius = SAND_RADIUS
        moment = pymunk.moment_for_circle(mass, 0, radius)

        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        self.shape.elasticity = 0
        self.shape.grain = self  
        self.color = color
        space.add(self.body, self.shape)

    def update_grid_position(self):
        self.grid_x = int(self.body.position.x // GRID_CELL_SIZE)
        self.grid_y = int(self.body.position.y // GRID_CELL_SIZE)
        if 0 <= self.grid_x < GRID_WIDTH and 0 <= self.grid_y < GRID_HEIGHT:
            sand_grid[self.grid_y][self.grid_x] = self

def create_sand_grain(x, y, color):
    return SandGrain(x, y, color)

def break_tetromino(tetromino):
    for block in tetromino.blocks:
        x, y = block.body.position
        space.remove(block.body, block.shape)
        # Create a grid of sand grains for each block
        grains_per_row = BLOCK_SIZE // (SAND_RADIUS * 2)
        grain_size = BLOCK_SIZE / grains_per_row
        for i in range(grains_per_row):
            for j in range(grains_per_row):
                gx = x - BLOCK_SIZE / 2 + grain_size / 2 + i * grain_size
                gy = y - BLOCK_SIZE / 2 + grain_size / 2 + j * grain_size
                create_sand_grain(gx, gy, block.color)

def remove_offscreen_grains():
    for shape in space.shapes[:]:
        if isinstance(shape, pymunk.Circle):
            if shape.body.position.y < -10:
                space.remove(shape.body, shape)

def update_sand_grid():
    # Clear the grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            sand_grid[y][x] = None

 
    for shape in space.shapes:
        if isinstance(shape, pymunk.Circle):
            grain = shape.grain  
            grain.update_grid_position()

def check_and_remove_full_lines():
    grains_to_remove = []
    for y in range(GRID_HEIGHT):
        color_counts = {}
        for x in range(GRID_WIDTH):
            grain = sand_grid[y][x]
            if grain:
                color = grain.color
                if color not in color_counts:
                    color_counts[color] = []
                color_counts[color].append(grain)
        for color, grains in color_counts.items():
            if len(grains) >= GRID_WIDTH:
                grains_to_remove.extend(grains)

   
    for grain in grains_to_remove:
        space.remove(grain.body, grain.shape)


def draw_objects():
    for shape in space.shapes:
        if isinstance(shape, pymunk.Poly):
            draw_rect(shape)
        elif isinstance(shape, pymunk.Circle):
            draw_circle(shape)

def draw_rect(shape):
    vertices = [v.rotated(shape.body.angle) + shape.body.position
                for v in shape.get_vertices()]
    points = [(int(p.x), int(SCREEN_HEIGHT - p.y)) for p in vertices]
    color = shape.block.color if hasattr(shape, 'block') else WHITE
    pygame.draw.polygon(screen, color, points)

def draw_circle(shape):
    position = int(shape.body.position.x), int(SCREEN_HEIGHT - shape.body.position.y)
    color = shape.grain.color if hasattr(shape, 'grain') else WHITE
    pygame.draw.circle(screen, color, position, int(shape.radius))

# Main game 
def main():
    create_static_floor()
    current_tetromino = Tetromino(random.choice(list(tetromino_shapes.keys())))
    drop_event = pygame.USEREVENT + 1
    pygame.time.set_timer(drop_event, 500)

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            elif event.type == drop_event:
                current_tetromino.move(0, -1)
                if current_tetromino.check_collision():
                    current_tetromino.move(0, 1)
                    current_tetromino.land()
                    break_tetromino(current_tetromino)
                    current_tetromino = Tetromino(
                        random.choice(list(tetromino_shapes.keys())))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_tetromino.move(-1, 0)
                    if current_tetromino.check_collision():
                        current_tetromino.move(1, 0)
                elif event.key == pygame.K_RIGHT:
                    current_tetromino.move(1, 0)
                    if current_tetromino.check_collision():
                        current_tetromino.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    current_tetromino.move(0, -1)
                    if current_tetromino.check_collision():
                        current_tetromino.move(0, 1)
                elif event.key == pygame.K_UP:
                    current_tetromino.rotate()
                    if current_tetromino.check_collision():
                        # Rotate back if collision detected
                        for _ in range(3):
                            current_tetromino.rotate()

        # Update physics
        try:
            space.step(1 / FPS)
        except Exception as e:
            print("Physics simulation error:", e)
            running = False
        update_sand_grid()
        check_and_remove_full_lines()
        remove_offscreen_grains()
        draw_objects()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
