import pygame, math, random, time
from queue import PriorityQueue

pygame.init()
gridw = 700
win = pygame.display.set_mode((gridw + 300, 700))
pygame.display.set_caption("pathfinding")
font = pygame.font.SysFont("Arial", 17)

white, black, gray = (255,255,255), (0,0,0), (200,200,200)
dgray, yellow, red = (80,80,80), (255,255,0), (220,50,50)
green, blue, orange = (0,200,0), (50,100,255), (255,165,0)

rows = 35
sz = gridw // rows

algo      = "A*"
heuristic = "Manhattan"
dynamic   = False
nodes_visited = 0
path_cost     = 0
exec_ms       = 0


class node:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.x = c * sz
        self.y = r * sz
        self.color = white
        self.nb = []

    def pos(self):
        return self.r, self.c

    def barrier(self):
        return self.color == black

    def draw(self):
        pygame.draw.rect(win, self.color, (self.x, self.y, sz, sz))

    def update_nb(self, grid):
        self.nb = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = self.r+dr, self.c+dc
            if 0 <= nr < rows and 0 <= nc < rows and not grid[nr][nc].barrier():
                self.nb.append(grid[nr][nc])


def make_grid():
    return [[node(r, c) for c in range(rows)] for r in range(rows)]


def hval(a, b):
    dr = abs(a[0]-b[0])
    dc = abs(a[1]-b[1])
    if heuristic == "Manhattan":
        return dr + dc
    return math.sqrt(dr**2 + dc**2)


def find_path(grid, start, end):
    global nodes_visited, exec_ms
    pq = PriorityQueue()
    pq.put((0, 0, start))
    seen = {start}
    came = {}
    g = {n: float("inf") for row in grid for n in row}
    g[start] = 0
    count = 0
    expanded = 0
    t0 = time.time()

    while not pq.empty():
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()

        cur = pq.get()[2]
        seen.discard(cur)

        if cur == end:
            path = []
            while cur in came:
                path.append(cur)
                cur = came[cur]
                cur.color = green
                draw(grid)
            end.color = orange
            start.color = blue
            nodes_visited = expanded
            exec_ms = round((time.time() - t0) * 1000)
            return path[::-1]

        if cur != start:
            cur.color = red
            expanded += 1

        for nb in cur.nb:
            ng = g[cur] + 1
            if ng < g[nb]:
                came[nb] = cur
                g[nb] = ng
                f = (ng + hval(nb.pos(), end.pos())) if algo == "A*" else hval(nb.pos(), end.pos())
                if nb not in seen:
                    count += 1
                    pq.put((f, count, nb))
                    seen.add(nb)
                    if nb != end:
                        nb.color = yellow
        draw(grid)

    return None


def draw(grid):
    win.fill(white)
    for row in grid:
        for n in row:
            n.draw()
    for i in range(rows):
        pygame.draw.line(win, gray, (0, i*sz), (gridw, i*sz))
        pygame.draw.line(win, gray, (i*sz, 0), (i*sz, gridw))
    pygame.draw.rect(win, dgray, (gridw, 0, 300, 700))
    lines = [
        ("algo =", algo),
        ("heuristic =", heuristic),
        ("dynamic =", "ON" if dynamic else "OFF"),
        ("",),
        ("nodes =", str(nodes_visited)),
        ("path cost =", str(path_cost)),
        ("time (ms) =", str(exec_ms)),
        ("",),
        ("[A] algo  [H] heuristic",),
        ("[D] dynamic  [M] maze",),
        ("[C] clear  [SPACE] start",),
        ("lclick = wall  rclick = erase",),
    ]
    for i, line in enumerate(lines):
        text = " ".join(line)
        win.blit(font.render(text, True, white), (gridw+15, 20+i*35))
    pygame.display.update()


def clicked_node(grid):
    mx, my = pygame.mouse.get_pos()
    if mx < gridw:
        return grid[my//sz][mx//sz]


def main():
    global algo, heuristic, dynamic, nodes_visited, path_cost, exec_ms
    grid = make_grid()
    start = grid[2][2]
    end = grid[rows-3][rows-3]
    start.color = blue
    end.color = orange
    path = []
    idx = 0
    moving = False
    clock = pygame.time.Clock()
    last_step = 0

    while True:
        clock.tick(60)
        draw(grid)

        if moving and path:
            now = time.time()
            if now - last_step >= 0.1:
                last_step = now

                if dynamic and random.random() < 0.05:
                    rn = grid[random.randint(0,rows-1)][random.randint(0,rows-1)]
                    if rn.color == white:
                        rn.color = black
                        if rn in path[idx:]:
                            cur = path[idx]
                            for row in grid:
                                for n in row:
                                    if n.color in [red, yellow, green] and n != cur and n != end:
                                        n.color = white
                            cur.color = blue
                            for row in grid:
                                for n in row:
                                    n.update_nb(grid)
                            new_path = find_path(grid, cur, end)
                            if new_path:
                                path = new_path
                                idx = 0
                                path_cost = len(path)
                            else:
                                moving = False

                if moving and idx < len(path):
                    if idx > 0:
                        path[idx-1].color = green
                    if path[idx] != end:
                        path[idx].color = blue
                    idx += 1
                else:
                    moving = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if not moving:
                if pygame.mouse.get_pressed()[0]:
                    n = clicked_node(grid)
                    if n and n.color not in [blue, orange]:
                        n.color = black
                elif pygame.mouse.get_pressed()[2]:
                    n = clicked_node(grid)
                    if n:
                        n.color = white

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        algo = "GBFS" if algo == "A*" else "A*"
                    if event.key == pygame.K_h:
                        heuristic = "Euclidean" if heuristic == "Manhattan" else "Manhattan"
                    if event.key == pygame.K_d:
                        dynamic = not dynamic
                    if event.key == pygame.K_c:
                        grid = make_grid()
                        start = grid[2][2]
                        end = grid[rows-3][rows-3]
                        start.color = blue
                        end.color = orange
                        nodes_visited = path_cost = exec_ms = 0
                    if event.key == pygame.K_m:
                        for row in grid:
                            for n in row:
                                if n.color == white and random.random() < 0.3:
                                    n.color = black
                    if event.key == pygame.K_SPACE:
                        for row in grid:
                            for n in row:
                                n.update_nb(grid)
                                if n.color in [red, yellow, green]:
                                    n.color = white
                        start.color = blue
                        end.color = orange
                        result = find_path(grid, start, end)
                        if result:
                            path = result
                            idx = 0
                            moving = True
                            last_step = time.time()
                            path_cost = len(path)

main()
