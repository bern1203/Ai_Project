import pygame
import sys

# Initialize pygame
pygame.init()

# Set screen dimensions
WIDTH, HEIGHT = 500, 500
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Grid")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)  # Character color

# Starting position of the character
char_x, char_y = 0, 0  # Top-left corner of the grid

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Move the character based on arrow key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and char_y > 0:  # Move up
                char_y -= 1
            if event.key == pygame.K_DOWN and char_y < GRID_SIZE - 1:  # Move down
                char_y += 1
            if event.key == pygame.K_LEFT and char_x > 0:  # Move left
                char_x -= 1
            if event.key == pygame.K_RIGHT and char_x < GRID_SIZE - 1:  # Move right
                char_x += 1

    # Fill screen with white
    screen.fill(WHITE)

    # Draw grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Draw the character
    character = pygame.Rect(char_x * CELL_SIZE, char_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, YELLOW, character)

    # Update display
    pygame.display.flip()