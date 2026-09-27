import sys

sys.path.append("src")

from core.domain import ALFA_BASE, Position
from core.environment import Environment
from core.search import astar, compare


def main():
    env = Environment(seed=1)
    start = Position(*ALFA_BASE[0])
    #goal = next(iter(env.minerals))
    #para pegar o rubi
    goal = list(env.minerals)[5]


    path, cost, expanded = astar(env, start, goal)
    results = compare(env, start, goal)

    env.show_with_path(path)

    print(f"alvo: {goal} | passos: {len(path) - 1} | custo: {cost} | expandidos: {expanded}")

    for name, result in results.items():
        print(f"{name}: custo {result['cost']}, {result['expanded']} nos, {result['time'] * 1000:.3f} ms")


if __name__ == "__main__":
    main()
