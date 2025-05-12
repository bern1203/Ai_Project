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

# Initialize game state

def generate_obstacle_clusters():
    clusters = [
        (1, 1), (4, 1), (7, 1),
        (1, 4), (4, 4), (7, 4),
        (1, 7), (4, 7), (7, 7)
    ]
    positions = set()
    for base_x, base_y in clusters:
        width, height = 2, 2
        if random.random() < 0.25:
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
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) not in obstacles and (x, y) != (0, 0) and (x, y) != (GRID_SIZE-1, GRID_SIZE-1):
                if random.random() < 0.1:
                    positions.add((x, y))
    return positions

def reset_game(new_map=False):
    global player_pos, obstacle_positions, trash_positions, original_trash_positions
    global fuel, trash_collected, ai_path, show_end_screen, last_ai_step_time
    global computer_play, ai_mode

    player_pos = [0, 0]
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

# Initial state
player_pos = [0, 0]
obstacle_positions = generate_obstacle_clusters()
trash_positions = generate_trash_positions(obstacle_positions)
original_trash_positions = set(trash_positions)
dumpster_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
fuel = FUEL_START
trash_collected = 0
computer_play = False
ai_path = []
last_ai_step_time = 0
show_end_screen = False
ai_mode = "astar"

# Button setup
button_rects = {
    "Play Again": pygame.Rect(WIDTH - 180, 100, 160, 40),
    "New Game": pygame.Rect(WIDTH - 180, 160, 160, 40),
    "Toggle A* AI": pygame.Rect(WIDTH - 180, 220, 160, 40),
    "Greedy AI": pygame.Rect(WIDTH - 180, 280, 160, 40)
}

def draw_grid():
    for x in range(0, GRID_SIZE * TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (GRID_SIZE * TILE_SIZE, y))

def draw_entities():
    for ox, oy in obstacle_positions:
        pygame.draw.rect(screen, GRAY, (ox*TILE_SIZE, oy*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for tx, ty in trash_positions:
        pygame.draw.circle(screen, GREEN, (tx*TILE_SIZE + TILE_SIZE//2, ty*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//4)
    dx, dy = dumpster_pos
    pygame.draw.rect(screen, BLUE, (dx*TILE_SIZE, dy*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    px, py = player_pos
    pygame.draw.rect(screen, RED, (px*TILE_SIZE, py*TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_ui():
    pygame.draw.rect(screen, LIGHT_GRAY, (GRID_SIZE*TILE_SIZE, 0, 200, HEIGHT))
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

def is_victory():
    return tuple(player_pos) == dumpster_pos and not trash_positions

def move_player(dx, dy):
    global fuel, trash_collected
    if fuel <= 0:
        return
    nx, ny = player_pos[0] + dx, player_pos[1] + dy
    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in obstacle_positions:
        player_pos[0], player_pos[1] = nx, ny
        fuel -= 1
        if (nx, ny) in trash_positions:
            trash_positions.remove((nx, ny))
            trash_collected += 1

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos):
    x, y = pos
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in obstacle_positions:
            yield (nx, ny)

def a_star(start, goal):
    open_set = [(0 + heuristic(start, goal), 0, start, [])]
    visited = set()
    while open_set:
        est_total, cost, current, path = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            return path + [current]
        for neighbor in get_neighbors(current):
            heapq.heappush(open_set, (cost + 1 + heuristic(neighbor, goal), cost + 1, neighbor, path + [current]))
    return []

def greedy_search(start, goal):
    open_set = [(heuristic(start, goal), start, [])]
    visited = set()
    while open_set:
        h, current, path = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            return path + [current]
        for neighbor in get_neighbors(current):
            heapq.heappush(open_set, (heuristic(neighbor, goal), neighbor, path + [current]))
    return []

def compute_full_ai_path():
    waypoints = list(trash_positions)
    best_path = []
    best_cost = float('inf')
    for perm in itertools.permutations(waypoints):
        path = []
        cost = 0
        current = tuple(player_pos)
        for point in perm:
            segment = a_star(current, point) if ai_mode == "astar" else greedy_search(current, point)
            if not segment:
                break
            cost += len(segment)
            path += segment[1:]
            current = point
        final_segment = a_star(current, dumpster_pos) if ai_mode == "astar" else greedy_search(current, dumpster_pos)
        if final_segment:
            cost += len(final_segment)
            path += final_segment[1:]
            if cost < best_cost:
                best_cost = cost
                best_path = path
    return best_path

# Main loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)
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
                    ai_path = compute_full_ai_path()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if button_rects["Play Again"].collidepoint(mx, my):
                reset_game(new_map=False)
            elif button_rects["New Game"].collidepoint(mx, my):
                reset_game(new_map=True)
            elif button_rects["Toggle A* AI"].collidepoint(mx, my):
                ai_mode = "astar"
                computer_play = True
                ai_path = compute_full_ai_path()
            elif button_rects["Greedy AI"].collidepoint(mx, my):
                ai_mode = "greedy"
                computer_play = True
                ai_path = compute_full_ai_path()

    if computer_play and ai_path and fuel > 0 and not show_end_screen:
        if current_time - last_ai_step_time >= AI_DELAY:
            next_step = ai_path.pop(0)
            dx = next_step[0] - player_pos[0]
            dy = next_step[1] - player_pos[1]
            move_player(dx, dy)
            last_ai_step_time = current_time

    if is_victory() and not show_end_screen:
        show_end_screen = True

    pygame.display.flip()

pygame.quit()
