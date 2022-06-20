from tkinter import messagebox, Tk
from venv import create
import pygame
import sys

# constants
WIN_WIDTH = 500
WIN_HEIGHT = 500

GRID_COLUMNS = 25
GRID_ROWS = 25
BOX_WIDTH = WIN_WIDTH // GRID_COLUMNS
BOX_HEIGHT = WIN_HEIGHT // GRID_ROWS

BACKDROP_COLOR = (0,0,0)
GRID_COLOR = (50, 50, 50)

class Box:
    def __init__(self, i, j) -> None:
        self.x = i
        self.y = j
    
    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x * BOX_WIDTH, self.y * BOX_HEIGHT, BOX_WIDTH - 2, BOX_HEIGHT - 2))

def create_grid(columns: int, rows: int) -> list:
    grid = []
    for i in range(columns):
        arr = []
        for j in range(rows):
            arr.append(Box(i, j))
        grid.append(arr)
    
    return grid
    

def main() -> None:
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")

    grid = create_grid(GRID_COLUMNS, GRID_ROWS)

    while True:
        for event in pygame.event.get():
            # quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        win.fill(BACKDROP_COLOR)

        for i in grid:
            for box in i:
                box.draw(win, GRID_COLOR)

        pygame.display.flip()

main()