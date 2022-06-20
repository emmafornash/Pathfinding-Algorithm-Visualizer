from tkinter import messagebox, Tk
import pygame
import sys

# constants
WIN_WIDTH = 500
WIN_HEIGHT = 500

def main() -> None:
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")
    while True:
        for event in pygame.event.get():
            # quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        win.fill((0,0,0))

        pygame.display.flip()

main()