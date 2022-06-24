from tkinter import messagebox, Tk
import pygame
import sys
import logging
import numpy as np
from button import Button
from enum import Enum

pygame.init()

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

# buttons
BASE_BUTTON_COLOR = '#acc9a9'
HOVERING_BUTTON_COLOR = '#FFFFFF'
BUTTON_IMG = pygame.transform.scale(pygame.image.load("assets/buttons/button_rect.png"), (240, 75))

FONT = pygame.font.Font("assets/fonts/font.ttf", 25)
DRAW_POS = (150, 100)
MANHATTAN_POS = (150, 200)
DIJKSTRA_POS = (150, 300)

class DRAW(Enum):
    START = 0
    WALL = 1
    TARGET = 2

class Box:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y
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

    # resets all values besides start to default
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
        pygame.draw.rect(win, color, (self.x * BOX_WIDTH, self.y * BOX_HEIGHT, BOX_WIDTH - 2, BOX_HEIGHT - 2))

    def set_neighbours(self, grid: list, columns: int, rows: int, all_eight: bool = True) -> None:
        if self.neighbours:
            self.neighbours = []

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

class Cursor(Box):
    def __init__(self, x, y):
        super().__init__(x, y)

    def move(self, x, y):
        self.x, self.y = x, y

    def __repr__(self) -> str:
        return (f'Cursor(x={self.x},y={self.y},start={self.start},wall={self.wall},' +
                f'target={self.target},queued={self.queued},visited={self.visited}')

# creates the grid for the algorithm to read from
def create_grid(columns: int, rows: int) -> list:
    grid = []
    for i in range(columns):
        arr = []
        for j in range(rows):
            arr.append(Box(i, j))
        grid.append(arr)
    return grid

# sets all neighbors within a grid
def set_neighbours(grid: list, columns: int, rows: int, alleight: bool = True) -> None:
    for i in grid:
        for box in i:
            box.set_neighbours(grid, columns, rows, alleight)

# resets all but start, walls and target by default
# if hard_reset is set to True, resets all but start
def reset(grid: list, alleight: bool, hard_reset: bool = False) -> None:
    for i in grid:
        for box in i:
            if hard_reset:
                box.hard_reset()
            else:
                box.reset()

    set_neighbours(grid, GRID_COLUMNS, GRID_ROWS, alleight)

# basic heuristic function for A*
def euclidean_dist(a: Box, b: Box) -> float:
    a_point = np.array((a.x, a.y))
    b_point = np.array((b.x, b.y))
    return np.linalg.norm(a_point - b_point)

# secondary basic heuristic function for just vertical and horizontal neighbors
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

    clock = pygame.time.Clock()

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    draw_state = DRAW.START

    cursor = Cursor(0, 0)
    cursor.start = True

    grid = create_grid(GRID_COLUMNS, GRID_ROWS)
    set_neighbours(grid, GRID_COLUMNS, GRID_ROWS, not manhattan)
    start_box = grid[0][0]
    start_box.start = True
    start_box.visited = True

    open_set = []
    open_set.append(start_box)

    path = []

    manhattan_button = Button(x=MANHATTAN_POS[0], y=MANHATTAN_POS[1], image=BUTTON_IMG, text_input="Euclidean", 
                                font=FONT, base_color=BASE_BUTTON_COLOR, hovering_color=HOVERING_BUTTON_COLOR)
    dijkstra_button = Button(x=DIJKSTRA_POS[0], y=DIJKSTRA_POS[1], image=BUTTON_IMG, text_input="A*", 
                                font=FONT, base_color=BASE_BUTTON_COLOR, hovering_color=HOVERING_BUTTON_COLOR)
    draw_state_button = Button(x=DRAW_POS[0], y=DRAW_POS[1], image=BUTTON_IMG, text_input="Start",
                                font=FONT, base_color=BASE_BUTTON_COLOR, hovering_color=HOVERING_BUTTON_COLOR)

    # screen with grid and visualization
    def grid_screen() -> None:
        nonlocal begin_search, target_box_set, searching, target_box, dijkstra, manhattan, clock, win, cursor, grid, start_box, open_set, path, draw_state

        pygame.display.set_caption("Pathfinding Visualizer")
        while True:
            # clock.tick(165)
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
                    elif event.buttons[2]:
                        grid[i][j].hard_reset()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # TODO: make this feel better before fully incorporating it
                    # if event.button == 1 and not grid[i][j].target and not grid[i][j].start:
                    #     grid[i][j].wall = not grid[i][j].wall
                    # set target
                    if event.button == 1 and searching:
                        match draw_state:
                            # set start point
                            case DRAW.START:
                                if not grid[i][j].wall and not grid[i][j].target:
                                    start_box.hard_reset()
                                    start_box = grid[i][j]
                                    start_box.start = True
                                    start_box.visited = True
                                    open_set = []
                                    open_set.append(start_box)
                            # add walls
                            case DRAW.WALL:
                                if not grid[i][j].start and not grid[i][j].target:
                                    grid[i][j].wall = True
                            # set target point
                            case DRAW.TARGET:
                                if not grid[i][j].wall and not grid[i][j].start:
                                    if target_box_set:
                                        target_box.target = False
                                    target_box = grid[i][j]
                                    target_box.target = True
                                    target_box_set = True
                    elif event.button == 3 and searching:
                        grid[i][j].hard_reset()
                # start algorithm
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not begin_search or not searching:
                            menu_screen()
                    elif event.key == pygame.K_s:
                        draw_state = DRAW.START
                    elif event.key == pygame.K_w:
                        draw_state = DRAW.WALL
                    elif event.key == pygame.K_t:
                        draw_state = DRAW.TARGET
                    elif event.key == pygame.K_r:
                        # resets evertyhing
                        reset(grid, not manhattan, True)
                        start_box = grid[0][0]
                        start_box.start = True
                        start_box.visited = True
                        open_set = []
                        open_set.append(start_box)
                        path = []
                        target_box_set = False
                        searching = True
                        begin_search = False
                    elif target_box_set:
                        # resets algorithm
                        if begin_search == True:
                            reset(grid, not manhattan)
                            open_set = []
                            open_set.append(start_box)
                            path = []
                        searching = True
                        begin_search = not begin_search

                cursor.move(i, j)
                cursor.hard_reset()
                match draw_state:
                    case DRAW.START:
                        cursor.start = True
                    case DRAW.WALL:
                        cursor.wall = True
                    case DRAW.TARGET:
                        cursor.target = True
                    case _:
                        pass
            
            # Dijkstra and A*
            if begin_search:
                set_neighbours(grid, GRID_COLUMNS, GRID_ROWS, not manhattan)
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
                        for neighbour in current_box.neighbours:
                            if not neighbour.queued and not neighbour.wall:
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

            # draws all assets
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
            
            if not begin_search:
                if cursor.start:
                    cursor.draw(win, START_COLOR)
                if cursor.wall:
                    cursor.draw(win, WALL_COLOR)
                if cursor.target:
                    cursor.draw(win, TARGET_COLOR)

            pygame.display.flip()

    # main menu screen
    def menu_screen() -> None:
        buttons = [manhattan_button, dijkstra_button, draw_state_button]

        nonlocal begin_search, target_box_set, searching, target_box, dijkstra, manhattan, clock, win, cursor, grid, start_box, open_set, path, draw_state

        pygame.display.set_caption("Menu")
        while True:
            for event in pygame.event.get():
                # mouse position and relative cell
                x, y = pygame.mouse.get_pos()

                # quit window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        grid_screen()
                if event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        button.change_color((x, y))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if manhattan_button.check_for_input((x, y)):
                        manhattan = not manhattan
                        # print(f'manhattan={manhattan}')
                        set_neighbours(grid, GRID_COLUMNS, GRID_ROWS, not manhattan)

                        if manhattan:
                            manhattan_button.change_text("Manhattan")
                        else:
                            manhattan_button.change_text("Euclidean")
                    if dijkstra_button.check_for_input((x, y)):
                        dijkstra = not dijkstra
                        # print(f'dijkstra={dijkstra}')

                        if dijkstra:
                            dijkstra_button.change_text("Dijkstra")
                        else:
                            dijkstra_button.change_text("A*")
                    if draw_state_button.check_for_input((x, y)):
                        match draw_state:
                            case DRAW.START:
                                draw_state = DRAW.WALL
                                draw_state_button.change_text("Wall")
                            case DRAW.WALL:
                                draw_state = DRAW.TARGET
                                draw_state_button.change_text("Target")
                            case DRAW.TARGET:
                                draw_state = DRAW.START
                                draw_state_button.change_text("Start")
                            case _:
                                pass


            win.fill(BACKDROP_COLOR)

            for button in buttons:
                button.draw(win)

            pygame.display.flip()

    grid_screen()

main()