import pygame
import sys
import random

# Set screen dimensions
width = 500
height = 600
grid = 10
cell = width // grid

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)  # Trash color
YELLOW = (255, 255, 0)  # Garbage truck color
RED = (255, 0, 0)  # House color
BLUE = (0, 0, 255)  # Button color
BLACK = (0, 0, 0)  # Text color

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

