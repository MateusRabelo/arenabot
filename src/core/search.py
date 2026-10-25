import time
import heapq
from collections import deque
from core.domain import *
from core.environment import wall, trap

infinity = float("inf")


def is_walkable(env, pos):
    if pos.x < 0 or pos.x >= env.width or pos.y < 0 or pos.y >= env.height:
        return False
    return env.grid[pos.y][pos.x] != wall


def walkable_neighbors(env, pos):
    return [n for n in pos.neighbors() if is_walkable(env, n)]


#custo de entrar na zona, armadilha custa o dobro
def step_cost(env, nxt):
    if env.grid[nxt.y][nxt.x] == trap:
        return GRAPH_COST_TRAP
    return GRAPH_COST_NORMAL


def rebuild_path(came_from, goal):
    path = [goal]
    while came_from[path[-1]] is not None:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


#a*: f = g + h, sendo g o custo acumulado e h a manhattan do domain
def astar(env, start, goal):
    #contador de desempate
    counter = 0
    frontier = [(start.manhattan_distance(goal), counter, 0, start)]

    cost_so_far = {start: 0}  #g de cada zona, menor custo ja encontrado
    came_from = {start: None}  #de onde cada zona veio
    closed = set()
    expanded = 0  #nos abertos

    while frontier:
        _, _, cost, current = heapq.heappop(frontier)

        if current == goal:
            return rebuild_path(came_from, goal), cost, expanded

        if current in closed:  #duplicado na fila
            continue
        closed.add(current)
        expanded += 1

        for nxt in walkable_neighbors(env, current):
            if nxt in closed:
                continue

            new_cost = cost + step_cost(env, nxt)
            if new_cost < cost_so_far.get(nxt, infinity):  #achou rota melhor pra nxt
                cost_so_far[nxt] = new_cost
                came_from[nxt] = current
                counter += 1
                f_next = new_cost + nxt.manhattan_distance(goal)
                heapq.heappush(frontier, (f_next, counter, new_cost, nxt))

    return None, infinity, expanded  #fila vazia: alvo inalcancavel


#bfs para comparar (ele pede)
def bfs(env, start, goal):
    queue = deque([start])
    came_from = {start: None}
    cost_so_far = {start: 0}
    expanded = 0

    while queue:
        current = queue.popleft()

        if current == goal:
            return rebuild_path(came_from, goal), cost_so_far[current], expanded
        expanded += 1

        for nxt in walkable_neighbors(env, current):
            if nxt not in came_from: 
                came_from[nxt] = current
                cost_so_far[nxt] = cost_so_far[current] + step_cost(env, nxt)
                queue.append(nxt)

    return None, infinity, expanded


def compare(env, start, goal):
    results = {}
    for name, algorithm in (("A*", astar), ("BFS", bfs)):
        begin = time.perf_counter()
        path, cost, expanded = algorithm(env, start, goal)
        elapsed = time.perf_counter() - begin
        results[name] = {"path": path, "cost": cost, "expanded": expanded, "time": elapsed}
    return results
