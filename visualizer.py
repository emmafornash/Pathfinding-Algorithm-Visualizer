from fcntl import LOCK_WRITE
from tkinter import messagebox, Tk
import pygame
import sys
import logging
import numpy as np

# constants
WIN_WIDTH = 500
WIN_HEIGHT = 500

GRID_COLUMNS = 25
GRID_ROWS = 25
BOX_WIDTH = WIN_WIDTH // GRID_COLUMNS
BOX_HEIGHT = WIN_HEIGHT // GRID_ROWS

# colors for grid creation
BACKDROP_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
START_COLOR = (0, 200, 200)
WALL_COLOR = (90, 90, 90)
TARGET_COLOR = (200, 200, 0)
VISITED_COLOR = (0, 200, 0)
QUEUED_COLOR = (200, 0, 0)
PATH_COLOR = (0, 0, 200)

class Box:
    def __init__(self, i, j) -> None:
        self.x = i
        self.y = j
        # maybe change this to an enum? might make the code more readable
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

        self.f = self.g = self.h = 0

    # resets all but start, target and wall
    def reset(self) -> None:
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

        self.f = self.g = self.h = 0

    # resets all values to default
    def hard_reset(self) -> None:
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

        self.f = self.g = self.h = 0
    
    def draw(self, win, color) -> None:
        # if self.queued:
        #     color = QUEUED_COLOR
        # elif self.visited:
        #     color = VISITED_COLOR
        # if self.start:
        #     color = START_COLOR
        # elif self.wall:
        #     color = WALL_COLOR
        # elif self.target:
        #     color = TARGET_COLOR
        # else:
        #     color = GRID_COLOR

        pygame.draw.rect(win, color, (self.x * BOX_WIDTH, self.y * BOX_HEIGHT, BOX_WIDTH - 2, BOX_HEIGHT - 2))

    def set_neighbours(self, grid: list, columns: int, rows: int, all_eight: bool = True) -> None:
        if all_eight:
            # finds all up to eight surrounding neighbours
            for i in range(max(0, self.x - 1), min(self.x + 2, rows)):
                for j in range(max(0, self.y - 1), min(self.y + 2, columns)):
                    if i != self.x or j != self.y:
                        self.neighbours.append(grid[i][j])
        else:
            # horizontal neighbours
            if self.x > 0:
                self.neighbours.append(grid[self.x - 1][self.y])
            if self.x < columns - 1:
                self.neighbours.append(grid[self.x + 1][self.y])

            # vertical neighbours
            if self.y > 0:
                self.neighbours.append(grid[self.x][self.y - 1])
            if self.y < rows - 1:
                self.neighbours.append(grid[self.x][self.y + 1])

    def __repr__(self) -> str:
        return (f'Box(x={self.x},y={self.y},start={self.start},wall={self.wall},' +
                f'target={self.target},queued={self.queued},visited={self.visited}')

# initially creates the grid for the algorithm to read from
def create_grid(columns: int, rows: int) -> list:
    grid = []
    for i in range(columns):
        arr = []
        for j in range(rows):
            arr.append(Box(i, j))
        grid.append(arr)
    return grid

# sets all neighbors within a grid
def set_neighbours(grid: list, columns: int, rows: int) -> None:
    for i in grid:
        for box in i:
            box.set_neighbours(grid, columns, rows)

# resets all but start, walls and target
def soft_reset(grid: list) -> None:
    for i in grid:
        for box in i:
            box.reset()

# basic heuristic function for A*
def euclidean_dist(a: Box, b: Box) -> float:
    a_point = np.array((a.x, a.y))
    b_point = np.array((b.x, b.y))
    return np.linalg.norm(a_point - b_point)

# secondary basic heuristic function for just verticle and horizontal neighbors
def manhattan_dist(a: Box, b: Box) -> float:
    return abs(a.x - b.x) + abs(a.y - b.y)

def main() -> None:
    begin_search = False
    target_box_set = False
    searching = True
    target_box = None

    # parameters for pathfinding algorithm
    dijkstra = False
    manhattan = False

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")

    grid = create_grid(GRID_COLUMNS, GRID_ROWS)
    set_neighbours(grid, GRID_COLUMNS, GRID_ROWS)
    start_box = grid[0][0]
    start_box.start = True
    start_box.visited = True

    closed_set = []
    open_set = []
    open_set.append(start_box)

    path = []

    while True:
        for event in pygame.event.get():
            # mouse position and relative cell
            x, y = pygame.mouse.get_pos()
            # need to change this to add resizable window support
            i = x // BOX_WIDTH
            j = y // BOX_HEIGHT

            # quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # mouse controls
            elif event.type == pygame.MOUSEMOTION:
                # draw wall
                if event.buttons[0] and not grid[i][j].target and not grid[i][j].start and searching:
                    grid[i][j].wall = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # TODO: make this feel better before fully incorporating it
                # if event.button == 1 and not grid[i][j].target and not grid[i][j].start:
                #     grid[i][j].wall = not grid[i][j].wall
                # set target
                if event.button == 3 and not grid[i][j].wall and not grid[i][j].start and searching:
                    if target_box_set:
                        target_box.target = False
                    target_box = grid[i][j]
                    target_box.target = True
                    target_box_set = True
            # start algorithm
            if event.type == pygame.KEYDOWN and target_box_set:
                # resets algorithm
                if begin_search == True:
                    soft_reset(grid)
                    set_neighbours(grid, GRID_COLUMNS, GRID_ROWS)
                    open_set = []
                    open_set.append(start_box)
                    closed_set = []
                    path = []
                searching = True
                begin_search = not begin_search
                # print(begin_search)
                # print(target_box)
        
        if begin_search:
            if len(open_set) and searching:
                lowest_box = 0
                for i in range(len(open_set)):
                    if open_set[i].f < open_set[lowest_box].f:
                        lowest_box = i
                current_box = open_set[lowest_box]
                current_box.visited = True
                if current_box == target_box:
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                else:
                    open_set.remove(current_box)
                    closed_set.append(current_box)
                    for neighbour in current_box.neighbours:
                        if not neighbour in closed_set and not neighbour.wall:
                            temp_g = current_box.g + 1

                            if (neighbour in open_set):
                                if temp_g < neighbour.g:
                                    neighbour.g = temp_g
                            else:
                                neighbour.g = temp_g
                                neighbour.queued = True
                                neighbour.prior = current_box
                                open_set.append(neighbour)

                            # heuristic handling
                            if not dijkstra:
                                if not manhattan:
                                    neighbour.h = euclidean_dist(neighbour, target_box)
                                else:
                                    neighbour.h = manhattan_dist(neighbour, target_box)
                            else:
                                neighbour.h = 0

                            neighbour.f = neighbour.g + neighbour.h
            else:
                if searching:
                    Tk().wm_withdraw()
                    messagebox.showinfo("No Solution", "There is no solution.")
                    searching = False


        win.fill(BACKDROP_COLOR)

        for i in grid:
            for box in i:
                box.draw(win, GRID_COLOR)

                if box.queued:
                    box.draw(win, QUEUED_COLOR)
                if box.visited:
                    box.draw(win, VISITED_COLOR)
                if box in path:
                    box.draw(win, PATH_COLOR)
                
                if box.start:
                    box.draw(win, START_COLOR)
                if box.wall:
                    box.draw(win, WALL_COLOR)
                if box.target:
                    box.draw(win, TARGET_COLOR)

        pygame.display.flip()

main()