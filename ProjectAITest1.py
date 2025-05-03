import pygame
import sys
import random

# Set screen dimensions
width = 500
height = 600
grid = 10
cell = width // grid
truck_x, truck_y = 0, 0  # Truck starting position
score = 0  # Initialize score

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)  # Trash color
YELLOW = (255, 255, 0)  # Garbage truck color
RED = (255, 0, 0)  # House color
BLUE = (0, 0, 255)  # Button color
BLACK = (0, 0, 0)  # Text color

house_positions = [(3,0), (4,0), (5,0), (6,0),
                    (1,1), (3,1), (4,1), (5,1), (6,1), (8,1),
                    (1,2), (8,2),
                    (4,3), (5,3),
                    (0,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (9,4),
                    (0, 5), (4,5), (5,5), (9,5),
                    (0, 7), (3,7), (6,7), (9,7),
                    (0, 8), (2,8), (3,8), (6,8), (7,8), (9,8),
                    (0,9), (4,9), (5,9), (9,9)]

trash_positions = [(random.randint(0, grid - 1), random.randint(0, grid - 1)) for _ in range(15)]
original_trash_positions = trash_positions.copy()  # Save the original trash layout for resetting

class Map:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x*size, y*size, size, size)
    def draw(self, screen, color, border=1):
        pygame.draw.rect(screen, color, self.rect, border)

class House:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x*size, y*size, size, size)
    def draw(self, screen, color, border=1):
        pygame.draw.rect(screen, color, self.rect, border)

class Trash:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x*size+size//4, y*size+size//4, size//2, size//2)
    def draw(self, screen, color, border=1):
        pygame.draw.rect(screen, color, self.rect, border)

class Truck:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x*size, y*size, size, size)
    def draw(self, screen, color, border=1):
        pygame.draw.rect(screen, color, self.rect, border)

class Button:
    def __init__(self, x, y, width= 150, height=40, text="",font=None, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(font, font_size)
    def draw(self, screen, color, text_color):
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, text_color)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                    self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def main():

    # Initialize pygame
    pygame.init()
    # Set up display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Garbage Truck Game")
    # # Set up map
    # map = Map(x, y, cell)
    # for m in map:
    #     m.draw(screen, GRAY)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        for row in range(grid):
                    for col in range(grid):
                        pygame.draw.rect(screen, GRAY, pygame.Rect(col * cell, row * cell, cell, cell), 1)
        pygame.display.flip()



    # # Set up houses
    # houses = [House(x, y, cell) for x in range(grid) for y in range(grid) if (x, y) in house_positions]
    # # Set up trash
    # trash = [Trash(x, y, cell) for x in range(grid) for y in range(grid) if (x, y) in trash_positions]
    # # Set up truck
    # truck = Truck(truck_x, truck_y, cell)
    # # Set up buttons
    # new_game_button = Button(50, height - 80, text="New Game")
    # play_again_button = Button(300, height - 80, text="Play Again")


    # Quit pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

  