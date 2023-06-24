from queue import PriorityQueue

import pygame

ROWS = 40
WIDTH = 800
NODE_WIDTH = WIDTH // ROWS

# make window
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("a*")

# colors
WHITE = 0xECEFF4
BLACK = 0x2E3440
PURPLE = 0xB48EAD
ORANGE = 0xD08770
GREY = 0xD8DEE9
LIGHT_GREY = 0xE5E9F0
TURQUOISE = 0x8FBCBB

class Node:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.x = row * NODE_WIDTH
        self.y = col * NODE_WIDTH
        self.color = WHITE

    def make_open(self) -> None:
        self.color = GREY

    def make_closed(self) -> None:
        self.color = LIGHT_GREY

    def is_barrier(self) -> bool:
        return self.color == BLACK

    def make_barrier(self) -> None:
        self.color = BLACK

    def make_path(self) -> None:
        self.color = PURPLE

    def make_start(self) -> None:
        self.color = ORANGE

    def make_end(self) -> None:
        self.color = TURQUOISE

    def reset(self) -> None:
        self.color = WHITE

    def draw(self) -> None:
        pygame.draw.rect(WIN, self.color, (self.x, self.y, NODE_WIDTH, NODE_WIDTH))

    def get_pos(self) -> tuple[int, int]:
        """get row and col"""
        return self.row, self.col

    def update_neighbors(self, grid: list[list]):
        """add all non-barrier adjacent nodes to neighbors array"""
        self.neighbors = []

        # top
        if self.row > 0:
            top_neighbor = grid[self.row - 1][self.col]
            if not top_neighbor.is_barrier():
                self.neighbors.append(top_neighbor)

        # bottom
        if self.row < ROWS - 1:
            bottom_neighbor = grid[self.row + 1][self.col]
            if not bottom_neighbor.is_barrier():
                self.neighbors.append(bottom_neighbor)

        # left
        if self.col > 0:
            left_neighbor = grid[self.row][self.col - 1]
            if not left_neighbor.is_barrier():
                self.neighbors.append(left_neighbor)

        # right
        if self.col < ROWS - 1:
            right_neighbor = grid[self.row][self.col + 1]
            if not right_neighbor.is_barrier():
                self.neighbors.append(right_neighbor)

def make_grid(rows: int) -> list[list]:
    """create 2d matrix of Node instances"""
    grid = []

    for row in range(rows):
        grid.append([])
        for col in range(rows):
            node = Node(row, col)
            grid[row].append(node)

    return grid

def draw(grid: list[list]) -> None:
    """draw nodes and gridlines"""
    WIN.fill(WHITE)

    # draw nodes
    for row in grid:
        for node in row:
            node.draw()

    # draw gridlines
    for i in range(ROWS):
        pygame.draw.line(WIN, GREY, (0, i * NODE_WIDTH), (WIDTH, i * NODE_WIDTH))
        for j in range(ROWS):
            pygame.draw.line(WIN, GREY, (j * NODE_WIDTH, 0), (j * NODE_WIDTH, WIDTH))

    pygame.display.update()

def get_clicked_pos(pos: tuple[int, int]) -> tuple[int, int]:
    """get row and col of clicked node"""
    x, y = pos
    row = x // NODE_WIDTH
    col = y // NODE_WIDTH
    return row, col

def get_heuristic_distance(p1: tuple[int, int], p2: tuple[int, int]) -> int:
    """get heuristic distance from p1 to p2"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def rebuild_path(grid: list[list], came_from: dict, curr: Node) -> None:
    """draw found path from start to end"""
    while curr in came_from:
        curr = came_from[curr]
        curr.make_path()
        draw(grid)

def a_star(grid: list[list], start: Node, end: Node):
    """a* algorithm"""

    count = 0
    open = PriorityQueue() # nodes to process
    open.put((0, count, start))
    open_set = {start} # nodes in open
    came_from = {} # map of Node to predecessor in path

    # map of Node to shortest distance from start to Node
    g_scores = {node: float("inf") for row in grid for node in row}
    g_scores[start] = 0

    # map of Node g_score[Node] + the heuristic distance from Node to end
    f_scores = {node: float("inf") for row in grid for node in row}
    f_scores[start] = get_heuristic_distance(start.get_pos(), end.get_pos())

    while not open.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        curr = open.get()[2]
        open_set.remove(curr)

        # search is finished
        if curr == end:
            rebuild_path(grid, came_from, end)
            start.make_start()
            end.make_end()
            return True
        
        for neighbor in curr.neighbors:
            temp_g_score = g_scores[curr] + 1

            if temp_g_score < g_scores[neighbor]:
                came_from[neighbor] = curr
                g_scores[neighbor] = temp_g_score
                f_scores[neighbor] = temp_g_score + get_heuristic_distance(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set:
                    count += 1
                    open.put((f_scores[neighbor], count, neighbor))
                    open_set.add(neighbor)
                    neighbor.make_open()

        draw(grid)

        # close visited node
        if curr != start:
            curr.make_closed()

    return False
    

def main():
    grid = make_grid(ROWS)

    # start and end nodes
    start = None
    end = None

    # event loop
    running = True
    searching = False
    while running:
        draw(grid)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ignore events if algorithm has started
            if searching:
                continue

            # left click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                # set start and end if not already set
                # if both are set, make barrier
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_barrier()

            # right click
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                # clear node
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                # start search
                if event.key == pygame.K_SPACE and start and end:
                    searching = True
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    a_star(grid, start, end)
                    searching = False

                # reset grid
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS)
                

    pygame.quit()
    
main()