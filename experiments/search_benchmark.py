import sys
import pathlib
import time
import statistics

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import Position, ALFA_BASE, BETA_BASE
from core.environment import Environment
from core.search import astar, bfs


def run_search_benchmark(num_seeds: int = 10):
    astar_nodes = []
    bfs_nodes = []
    astar_costs = []
    bfs_costs = []
    astar_times = []
    bfs_times = []

    for s in range(1, num_seeds + 1):
        env = Environment(seed=s)
        start = Position(*ALFA_BASE[0])

        for target in env.minerals.keys():
            t0 = time.perf_counter()
            p_a, c_a, exp_a = astar(env, start, target)
            t_a = (time.perf_counter() - t0) * 1000

            t1 = time.perf_counter()
            p_b, c_b, exp_b = bfs(env, start, target)
            t_b = (time.perf_counter() - t1) * 1000

            if p_a is not None and p_b is not None:
                astar_nodes.append(exp_a)
                bfs_nodes.append(exp_b)
                astar_costs.append(c_a)
                bfs_costs.append(c_b)
                astar_times.append(t_a)
                bfs_times.append(t_b)

    total_instances = len(astar_nodes)
    avg_nodes_a = statistics.mean(astar_nodes)
    avg_nodes_b = statistics.mean(bfs_nodes)
    avg_cost_a = statistics.mean(astar_costs)
    avg_cost_b = statistics.mean(bfs_costs)
    avg_time_a = statistics.mean(astar_times)
    avg_time_b = statistics.mean(bfs_times)

    saved_nodes = avg_nodes_b - avg_nodes_a
    pct_saved = (saved_nodes / avg_nodes_b) * 100

    print("=" * 76)
    print("BENCHMARK DE NAVEGAÇÃO: A* vs BUSCA EM LARGURA")
    print("=" * 76)
    print(f"Total de rotas avaliadas: {total_instances} pares de busca (10 arenas distintas)")
    print("-" * 76)
    print(f"{'Métrica':<30} | {'A* (Heurístico)':<18} | {'BFS (Referência)':<18}")
    print("-" * 76)
    print(f"{'Média de Nós Expandidos':<30} | {avg_nodes_a:<18.2f} | {avg_nodes_b:<18.2f}")
    print(f"{'Custo Médio do Caminho':<30} | {avg_cost_a:<18.2f} | {avg_cost_b:<18.2f}")
    print(f"{'Tempo Médio (ms)':<30} | {avg_time_a:<18.3f} | {avg_time_b:<18.3f}")
    print("-" * 76)
    print(f"Eficiência do A*: Redução de {pct_saved:.1f}% nos nós expandidos em relação ao BFS")
    print("=" * 76)


if __name__ == "__main__":
    run_search_benchmark(num_seeds=5)
