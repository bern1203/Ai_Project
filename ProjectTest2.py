import pygame
import random
import heapq
#import time
import itertools

# Config
GRID_SIZE = 10
TILE_SIZE = 64
WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE + 200, GRID_SIZE * TILE_SIZE  # Extra width for side panel
FPS = 60
FUEL_START = 100
AI_DELAY = 150  # milliseconds between AI steps

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

player_image = pygame.image.load("truck.png")#.convert_alpha()
player_image = pygame.transform.scale(player_image, (TILE_SIZE + 30, TILE_SIZE))
player_direction = 180  # 0 = Up, 90 = Left, 180 = Down, -90 = Right

trash_image = pygame.image.load("trashcan.png")#.convert_alpha()
trash_image = pygame.transform.scale(trash_image, (TILE_SIZE, TILE_SIZE))

house_image = pygame.image.load("house.png")#.convert_alpha()
house_image = pygame.transform.scale(house_image, (TILE_SIZE, TILE_SIZE))

dumpster_image = pygame.image.load("Dumpster.webp")#.convert_alpha()
dumpster_image = pygame.transform.scale(dumpster_image, (TILE_SIZE, TILE_SIZE))

# Initialize game state

def generate_obstacle_clusters():
    clusters = [
        (1, 1), (4, 1), (7, 1),
        (1, 4), (4, 4), (7, 4),
        (1, 7), (4, 7), (7, 7)
    ]
    positions = set()

    num_to_expand = random.randint(5, 9)
    expanded_indices = set(random.sample(range(len(clusters)), num_to_expand))

    for idx, (base_x, base_y) in enumerate(clusters):
        width, height = 2, 2
        if idx in expanded_indices:
            if random.choice([True, False]):
                if base_x + 2 < GRID_SIZE:
                    width = 3
            else:
                if base_y + 2 < GRID_SIZE:
                    height = 3
        for dx in range(width):
            for dy in range(height):
                x, y = base_x + dx, base_y + dy
                if (x, y) != (0, 0):
                    positions.add((x, y))
    return positions

def generate_trash_positions(obstacles):
    positions = set()
    num_trash = random.randint(5, 10)
    attempts = 0
    while len(positions) < num_trash and attempts < 100:
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        if (x, y) not in obstacles and (x, y) != (0, 0) and (x, y) != (GRID_SIZE-1, GRID_SIZE-1):
            positions.add((x, y))
        attempts += 1
    return positions

def reset_game(new_map=False):
    global player_pos, obstacle_positions, trash_positions, original_trash_positions
    global fuel, trash_collected, ai_path, show_end_screen, last_ai_step_time
    global computer_play, ai_mode

    player_pos = [GRID_SIZE - 1, 0]  # Start at top-right
    if new_map:
        obstacle_positions = generate_obstacle_clusters()
        trash_positions = generate_trash_positions(obstacle_positions)
        original_trash_positions = set(trash_positions)
    else:
        trash_positions = set(original_trash_positions)
    fuel = FUEL_START
    trash_collected = 0
    ai_path = []
    show_end_screen = False
    last_ai_step_time = pygame.time.get_ticks()
    computer_play = False
    ai_mode = "astar"

player_pos = [GRID_SIZE - 1, 0]  # Start at top-right corner
obstacle_positions = generate_obstacle_clusters()
trash_positions = generate_trash_positions(obstacle_positions)
original_trash_positions = set(trash_positions)
dumpster_pos = (GRID_SIZE - 1, 0)  # Dumpster also at top-right corner
fuel = FUEL_START
trash_collected = 0
computer_play = False
ai_path = []
last_ai_step_time = 0
show_end_screen = False
ai_mode = "astar"

button_rects = {
    "Play Again": pygame.Rect(WIDTH - 180, 100, 160, 40),
    "New Game": pygame.Rect(WIDTH - 180, 160, 160, 40),
    "A* AI": pygame.Rect(WIDTH - 180, 220, 160, 40),
    "Random AI": pygame.Rect(WIDTH - 180, 280, 160, 40)
}

def draw_grid():
    for x in range(0, GRID_SIZE * TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (GRID_SIZE * TILE_SIZE, y))

def draw_entities():
    for ox, oy in obstacle_positions:
        house = house_image.get_rect(topleft=(ox * TILE_SIZE, oy * TILE_SIZE))
        screen.blit(house_image, house.topleft)
    for tx, ty in trash_positions:
        trash = trash_image.get_rect(topleft=(tx * TILE_SIZE, ty * TILE_SIZE))
        screen.blit(trash_image, trash.topleft)

    dx, dy = dumpster_pos
    dumpster = dumpster_image.get_rect(topleft=(dx * TILE_SIZE, dy * TILE_SIZE))
    screen.blit(dumpster_image, dumpster.topleft)

    rotated_image = pygame.transform.rotate(player_image, player_direction)
    px, py = player_pos
    rotated_rect = rotated_image.get_rect(center=(px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(rotated_image, rotated_rect.topleft)

def draw_ui():
    pygame.draw.rect(screen, WHITE, (GRID_SIZE*TILE_SIZE, 0, 200, HEIGHT))
    if show_end_screen:
        msg = font.render(f"Victory! Score: {fuel + trash_collected}", True, BLACK)
        screen.blit(msg, (WIDTH - 180, 20))
    else:
        screen.blit(font.render(f"Fuel: {fuel}", True, BLACK), (WIDTH - 180, 20))
        screen.blit(font.render(f"Trash: {trash_collected}", True, BLACK), (WIDTH - 180, 50))
        screen.blit(font.render(f"AI: {'On' if computer_play else 'Off'} ({ai_mode})", True, BLACK), (WIDTH - 180, 80))

    for label, rect in button_rects.items():
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        screen.blit(font.render(label, True, BLACK), (rect.x + 10, rect.y + 10))

def move_player(dx, dy):
    global fuel, trash_collected, player_direction
    if fuel <= 0:
        return
    nx, ny = player_pos[0] + dx, player_pos[1] + dy
    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in obstacle_positions:
        player_pos[0], player_pos[1] = nx, ny
        fuel -= 1
        if (nx, ny) in trash_positions:
            trash_positions.remove((nx, ny))
            trash_collected += 1

        if dx == 1:
            player_direction = 0
        elif dx == -1:
            player_direction = 180
        elif dy == 1:
            player_direction = -90
        elif dy == -1:
            player_direction = 90

def goal_state():
    return tuple(player_pos) == dumpster_pos and not trash_positions

def heuristic(current, remaining_trash):
    if remaining_trash:
        return min(abs(current[0] - tx) + abs(current[1] - ty) for tx, ty in remaining_trash)
    else:
        return abs(current[0] - dumpster_pos[0]) + abs(current[1] - dumpster_pos[1])

def successors(pos):
    x, y = pos
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in obstacle_positions:
            yield (nx, ny)

# A* Algorithm
def astar_search(start, remaining_trash):
    frontier = [(0, 0, start, [], frozenset(remaining_trash))]
    visited = set()

    while frontier:
        priority, cost, current_pos, path, remaining = heapq.heappop(frontier)

        if (current_pos, remaining) in visited:
            continue
        visited.add((current_pos, remaining))

        new_path = path + [current_pos]
        new_remaining = set(remaining)
        if current_pos in new_remaining:
            new_remaining.remove(current_pos)

        if not new_remaining and current_pos == dumpster_pos:
            return new_path

        for neighbor in successors(current_pos):
            h = heuristic(neighbor, new_remaining)
            g = cost + 1
            f = g + h
            heapq.heappush(frontier, (f, g, neighbor, new_path, frozenset(new_remaining)))

    return []

# Greedy Algorithm
def greedy_search(start, remaining_trash):
    frontier = [(0, start, [], frozenset(remaining_trash))]
    visited = set()

    while frontier:
        _, current_pos, path, remaining = heapq.heappop(frontier)

        if (current_pos, remaining) in visited:
            continue
        visited.add((current_pos, remaining))

        new_path = path + [current_pos]
        new_remaining = set(remaining)
        if current_pos in new_remaining:
            new_remaining.remove(current_pos)

        if not new_remaining and current_pos == dumpster_pos:
            return new_path

        for neighbor in successors(current_pos):
            h = heuristic(neighbor, new_remaining)
            heapq.heappush(frontier, (h, neighbor, new_path, frozenset(new_remaining)))

    return []

def compute_ai_path():
    if ai_mode == "astar":
        return astar_search(tuple(player_pos), trash_positions)
    elif ai_mode == "greedy/random":
        return greedy_search(tuple(player_pos), trash_positions)
    return []

running = True
while running:
    clock.tick(FPS)
    screen.fill(LIGHT_GRAY)
    draw_grid()
    draw_entities()
    draw_ui()

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not show_end_screen:
            if event.key == pygame.K_UP:
                move_player(0, -1)
            elif event.key == pygame.K_DOWN:
                move_player(0, 1)
            elif event.key == pygame.K_LEFT:
                move_player(-1, 0)
            elif event.key == pygame.K_RIGHT:
                move_player(1, 0)
            elif event.key == pygame.K_c:
                computer_play = not computer_play
                if computer_play:
                    ai_path = compute_ai_path()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if button_rects["Play Again"].collidepoint(mx, my):
                reset_game(new_map=False)
            elif button_rects["New Game"].collidepoint(mx, my):
                reset_game(new_map=True)
            elif button_rects["A* AI"].collidepoint(mx, my):
                ai_mode = "astar"
                computer_play = True
                ai_path = compute_ai_path()
            elif button_rects["Random AI"].collidepoint(mx, my):
                ai_mode = "greedy/random"
                computer_play = True
                ai_path = compute_ai_path()

    if computer_play and ai_path and fuel > 0 and not show_end_screen:
        if current_time - last_ai_step_time >= AI_DELAY:
            next_step = ai_path.pop(0)
            dx = next_step[0] - player_pos[0]
            dy = next_step[1] - player_pos[1]
            move_player(dx, dy)
            last_ai_step_time = current_time
            if not ai_path:
                ai_path = compute_ai_path()

    if goal_state() and not show_end_screen:
        show_end_screen = True

    pygame.display.flip()

pygame.quit()
