import pygame
from queue import PriorityQueue

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags = pygame.HIDDEN)

GREEN = (0, 255, 0)  # in open list
BLUE = (0, 0, 255)  # in closed list
YELLOW = (255, 255, 0)  # start
WHITE = (255, 255, 255)  # not visited yet
BLACK = (0, 0, 0)  # wall
PURPLE = (128, 0, 128)  # goal
GREY = (128, 128, 128)  # grid
TURQUOISE = (246, 128, 30)  # is path

start_image = pygame.image.load('../images/start.jpg')
anchor_image = pygame.image.load('../images/anchor.jpg')
end_image = pygame.image.load('../images/end.png')

instruction = '''This tool implements some best-first-search algorithms, like A*.
Your first click sets the start point,
your second click sets the goal.
After that, every further click creates a barrier.
If you click with your scroll wheel, you can add an anchor.
These anchors are subgoals which are visited before the goal.
With the left and right arrow you can switch between variants of the algorithm.
If you want to clear the board press "r" on your keyboard.
This clears everything but the start, the goal, the barriers and the anchors, 
so you can retry the same problem again wit the same or a different algorithm.
Press "r" again to clear everything.
If you have selected a start and a goal point you can press the space bar to start the search.
Enjoy!'''

class Node:
    def __init__(self, row, column, width, total_rows):
        self.row = row
        self.col = column
        self.x = row * width
        self.y = column * width
        self.colour = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.anchor_number = 0

    def reset(self):
        self.colour = WHITE

    def get_pos(self):
        return self.col, self.row

    def get_colour(self):
        return self.colour

    def draw(self, win):
        if self.is_start():
            img = pygame.transform.scale(start_image, (self.width, self.width))
            win.blit(img, (self.x, self.y, self.width, self.width))
        elif self.is_end():
            img = pygame.transform.scale(end_image, (self.width, self.width))
            win.blit(img, (self.x, self.y, self.width, self.width))
        elif self.is_anchor():
            rect = pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))
            img = pygame.transform.scale(anchor_image, (self.width, self.width))
            win.blit(img, (self.x, self.y, self.width, self.width))
        else:
            pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
            self.neighbors.append(grid[self.row][self.col - 1])

    def is_start(self):
        return self.colour == YELLOW

    def make_start(self):
        self.colour = YELLOW

    def is_end(self):
        return self.colour == PURPLE

    def make_end(self):
        self.colour = PURPLE

    def is_closed(self):
        return self.colour == BLUE

    def make_closed(self):
        self.colour = BLUE

    def is_wall(self):
        return self.colour == BLACK

    def make_wall(self):
        self.colour = BLACK

    def is_open(self):
        return self.colour == GREEN

    def make_open(self):
        self.colour = GREEN

    def is_anchor(self):
        return self.colour == GREY

    def make_anchor(self, number):
        self.colour = GREY
        self.anchor_number = number

    def make_path(self):
        self.colour = TURQUOISE

    def is_path(self):
        return self.colour == TURQUOISE

# manhattan : abs(x1-x2)+abs(y1-y2)
def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for i in range(rows):
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def get_rows():
    while True:
        msg = input("Please enter the number of rows between 20 and 100: ")
        try:
            if type(int(msg)) is int and int(msg) >= 20 and int(msg) <= 100:
                return abs(int(msg))
        except:
            print("invalid input")


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def f_value(algo, node, end, g_score):
    if algo == "A-star":
        return g_score + distance(node.get_pos(), end.get_pos())
    elif algo == "Greedy best first search":
        return distance(node.get_pos(), end.get_pos())
    elif algo == "Uniform cost search":
        return g_score
    elif algo == "Weighted A-star with weight 2":
        return g_score + 2 * distance(node.get_pos(), end.get_pos())
    elif algo == "Weighted A-star with weight 10":
        return g_score + 10 * distance(node.get_pos(), end.get_pos())
    elif algo == "Weighted A-star with weight 25":
        return g_score + 25 * distance(node.get_pos(), end.get_pos())

def best_first_search(draw, grid, start, end, anchors, algo):
    count = 0  # for tie breaks-> same f value, prefer count
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = distance(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]  # gets just the node
        open_set_hash.remove(current)

        if current == end:
            if end in anchors:
                end.make_anchor(end.anchor_number)
            else:
                end.make_end()
            reconstruct_path(came_from, end, draw)
            if start in anchors:
                start.make_anchor(start.anchor_number)
            else:
                start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1  # 1 bc node distance is always 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = f_value(algo, neighbor, end, temp_g_score)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not neighbor.is_path() and neighbor not in anchors and neighbor != start:
                        neighbor.make_open()
        draw()

        if current != start and not current.is_path() and current not in anchors:
            current.make_closed()
    return False

def main(win, width):
    algos = ["A-star", "Greedy best first search", "Uniform cost search", "Weighted A-star with weight 2",
             "Weighted A-star with weight 10", "Weighted A-star with weight 25"]
    algo_index = 0
    msg = ""
    while msg != "y":
        print(instruction)
        msg = input("Do you want to continue? [y/n]")
        if msg == "n":
            pygame.quit()
            exit(0)
    ROWS = get_rows()
    window_size = win.get_height()
    win = pygame.display.set_mode((window_size, window_size), flags = pygame.SHOWN)
    grid = make_grid(ROWS, width)
    start = None
    anchors = []
    end = None
    run = True
    started = False
    is_clear = False
    algo = algos[algo_index]
    pygame.display.set_caption(algo)

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                is_clear = False
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                node = grid[row][col]
                if not start:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_wall()

            elif pygame.mouse.get_pressed()[1]:
                is_clear = False
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                node = grid[row][col]
                if node != start and node != end and not node.is_wall():
                    anchors.append(node)
                    node.make_anchor(len(anchors))

            elif pygame.mouse.get_pressed()[2]:
                is_clear = False
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                node = grid[row][col]
                if node == start:
                    start = None
                if node == end:
                    end = None
                if node in anchors:
                    anchors.remove(node)
                    node.anchor_number = 0
                node.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started and start != None and end != None:
                    is_clear = False
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    if len(anchors) == 0:
                        best_first_search(lambda: draw(win, grid, ROWS, width), grid, start, end, anchors, algo)
                    elif len(anchors) == 1:
                        best_first_search(lambda: draw(win, grid, ROWS, width), grid, start, anchors[0], anchors, algo)
                        best_first_search(lambda: draw(win, grid, ROWS, width), grid, anchors[0], end, anchors, algo)
                    else:
                        for i in range(len(anchors)):
                            if i == 0:
                                best_first_search(lambda: draw(win, grid, ROWS, width), grid, start, anchors[i],
                                                  anchors, algo)
                            elif i == len(anchors) - 1:
                                best_first_search(lambda: draw(win, grid, ROWS, width), grid, anchors[i - 1],
                                                  anchors[i], anchors, algo)
                                best_first_search(lambda: draw(win, grid, ROWS, width), grid, anchors[i], end, anchors,
                                                  algo)
                            else:
                                best_first_search(lambda: draw(win, grid, ROWS, width), grid, anchors[i - 1],
                                                  anchors[i], anchors, algo)

                if event.key == pygame.K_r:
                    if is_clear:
                        for row in grid:
                            for node in row:
                                node.reset()
                        end = None
                        start = None
                        anchors = []
                        deleted_once = False
                    else:
                        for row in grid:
                            for node in row:
                                if not node.is_start() and not node.is_end() and not node.is_anchor() and not node.is_wall():
                                    node.reset()
                        is_clear = True

                if event.key == pygame.K_RIGHT:
                    if algo_index < len(algos) - 1:
                        algo_index += 1
                        algo = algos[algo_index]
                        pygame.display.set_caption(algo)

                if event.key == pygame.K_LEFT:
                    if algo_index > 0:
                        algo_index -= 1
                        algo = algos[algo_index]
                        pygame.display.set_caption(algo)
    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)
