from tkinter import messagebox, Tk
import pygame
import sys
import logging

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
        # maybe add a way to get all surrounding blocks as neighbors instead of just four?
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

def create_grid(columns: int, rows: int) -> list:
    grid = []
    for i in range(columns):
        arr = []
        for j in range(rows):
            arr.append(Box(i, j))
        grid.append(arr)
    
    return grid

def set_neighbours(grid: list, columns: int, rows: int) -> None:
    for i in grid:
        for box in i:
            box.set_neighbours(grid, columns, rows)

def main() -> None:
    begin_search = False
    target_box_set = False
    searching = True
    target_box = None

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")

    grid = create_grid(GRID_COLUMNS, GRID_ROWS)
    set_neighbours(grid, GRID_COLUMNS, GRID_ROWS)
    start_box = grid[0][0]
    start_box.start = True
    start_box.visited = True
    print([(box.x, box.y) for box in start_box.neighbours])

    box_queue = []
    box_queue.append(start_box)

    path = []

    while True:
        for event in pygame.event.get():
            # quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # mouse controls
            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                i = x // BOX_WIDTH
                j = y // BOX_HEIGHT
                # print(i, j)
                # draw wall
                if event.buttons[0]:
                    grid[i][j].wall = True
                # set target
                if event.buttons[2] and not target_box_set:
                    target_box = grid[i][j]
                    target_box.target = True
                    target_box_set = True
            # start algorithm
            if event.type == pygame.KEYDOWN and target_box_set:
                begin_search = True
        
        if begin_search:
            if len(box_queue) > 0 and searching:
                current_box = box_queue.pop(0)
                current_box.visited = True
                if current_box == target_box:
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                else:
                    for neighbour in current_box.neighbours:
                        if not neighbour.queued and not neighbour.wall:
                            neighbour.queued = True
                            neighbour.prior = current_box
                            box_queue.append(neighbour)
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