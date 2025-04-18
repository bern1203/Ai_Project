import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Saves of different maps
Map1 = [(1,1), (2,1), (4,1), (5,1), (7,1), (8,1),
        (1,2), (2,2), (4,2), (5,2), (7,2), (8,2),
        (1,3), (2,3), (4,3), (5,3), (7,3), (8,3),
        (0, 5), (1,5), (3,5), (4,5), (5,5), (6,5), (8,5), (9,5),
        (0, 6), (1,6), (3,6), (4,6), (5,6), (6,6), (8,6), (9,6),
        (1, 8), (2,8), (4,8), (5,8), (7,8), (8,8),
        (4,9), (5,9)]



# Set screen dimensions and layout
WIDTH, HEIGHT = 500, 600  # Extra height for the button area
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neighborhood Cleanup")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)  # Trash color
YELLOW = (255, 255, 0)  # Garbage truck color
RED = (255, 0, 0)  # House color
BLUE = (0, 0, 255)  # Button color
BLACK = (0, 0, 0)  # Text color

# Function to reset the game for the same map
def reset_game():
    global truck_x, truck_y, score, trash_positions
    truck_x, truck_y = 0, 0  # Reset truck position
    score = 0  # Reset score
    trash_positions = original_trash_positions.copy()  # Restore original trash positions

# Function to generate a new map
def new_game():
    global truck_x, truck_y, score, trash_positions, house_positions, original_trash_positions
    truck_x, truck_y = 0, 0  # Reset truck position
    score = 0  # Reset score
    # Generate new random trash positions
    trash_positions = [(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(15)]
    original_trash_positions = trash_positions.copy()
    # This is where to add the houses 
    house_positions = [(3,0), (4,0), (5,0), (6,0),
                       (1,1), (3,1), (4,1), (5,1), (6,1), (8,1),
                       (1,2), (8,2),
                       (4,3), (5,3),
                       (0,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (9,4),
                       (0, 5), (4,5), (5,5), (9,5),
                       (0, 7), (3,7), (6,7), (9,7),
                       (0, 8), (2,8), (3,8), (6,8), (7,8), (9,8),
                       (0,9), (4,9), (5,9), (9,9)]

# Initial trash and house positions (fixed for competition)
trash_positions = [(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(15)]
original_trash_positions = trash_positions.copy()  # Save the original trash layout for resetting
house_positions = [(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(10)]  # Initial house locations
score = 0  # Initialize score
truck_x, truck_y = 0, 0  # Truck's starting position

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Move the truck based on arrow keys
        if event.type == pygame.KEYDOWN:
            new_x, new_y = truck_x, truck_y
            if event.key == pygame.K_UP and truck_y > 0:
                new_y -= 1
            if event.key == pygame.K_DOWN and truck_y < GRID_SIZE - 1:
                new_y += 1
            if event.key == pygame.K_LEFT and truck_x > 0:
                new_x -= 1
            if event.key == pygame.K_RIGHT and truck_x < GRID_SIZE - 1:
                new_x += 1

            # Check if new position is impassable (house)
            if (new_x, new_y) not in house_positions:
                truck_x, truck_y = new_x, new_y
                score -= 1  # Lose 1 point for emissions

        # Handle mouse clicks for buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check "New Game" button
            if 50 <= mouse_x <= 200 and HEIGHT - 80 <= mouse_y <= HEIGHT - 40:
                new_game()
            # Check "Play Again" button
            if 300 <= mouse_x <= 450 and HEIGHT - 80 <= mouse_y <= HEIGHT - 40:
                reset_game()

    # Check for trash collection
    if (truck_x, truck_y) in trash_positions:
        trash_positions.remove((truck_x, truck_y))
        score += 2  # Gain 2 points for picking up trash

    # Fill screen with white
    screen.fill(WHITE)

    # Draw grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Draw trash
    for tx, ty in trash_positions:
        trash = pygame.Rect(tx * CELL_SIZE + CELL_SIZE // 4, ty * CELL_SIZE + CELL_SIZE // 4,
                            CELL_SIZE // 2, CELL_SIZE // 2)
        pygame.draw.rect(screen, GREEN, trash)

    # Draw houses
    for hx, hy in house_positions:
        house = pygame.Rect(hx * CELL_SIZE, hy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, house)

    # Draw the garbage truck
    truck = pygame.Rect(truck_x * CELL_SIZE, truck_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, YELLOW, truck)

    # Draw buttons
    # "New Game" button
    pygame.draw.rect(screen, BLUE, (50, HEIGHT - 80, 150, 40))
    font = pygame.font.Font(None, 30)
    new_game_text = font.render("New Game", True, BLACK)
    screen.blit(new_game_text, (75, HEIGHT - 70))

    # "Play Again" button
    pygame.draw.rect(screen, BLUE, (300, HEIGHT - 80, 150, 40))
    play_again_text = font.render("Play Again", True, BLACK)
    screen.blit(play_again_text, (325, HEIGHT - 70))

    # Display the score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()