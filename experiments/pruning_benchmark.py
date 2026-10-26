import sys
import pathlib
import time

_root_dir = str(pathlib.Path(__file__).resolve().parent.parent)
_src_dir = str(pathlib.Path(__file__).resolve().parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import Position, MineralType
from core.environment import Environment
from strategy.minimax import choose_best_target_minimax


def run_pruning_benchmark():
    env = Environment(seed=42)
    p_alfa = Position(0, 0)
    p_beta = Position(14, 8)

    subset_minerals = dict(list(env.minerals.items())[:5])

    depths = [2, 4, 6]

    print("=" * 72)
    print("BENCHMARK DO MINIMAX")
    print("=" * 72)
    print(f"{'Profundidade (d)':<18} | {'Sem Poda':<12} | {'Com Poda':<12} | {'Economia':<10} | {'Redução (%)':<10}")
    print("-" * 72)

    for d in depths:
        t0 = time.perf_counter()
        tgt_no_prune, nodes_no_prune = choose_best_target_minimax(
            alfa_pos=p_alfa,
            beta_pos=p_beta,
            available_minerals=subset_minerals,
            depth=d,
            use_pruning=False,
        )
        time_no_prune = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        tgt_prune, nodes_prune = choose_best_target_minimax(
            alfa_pos=p_alfa,
            beta_pos=p_beta,
            available_minerals=subset_minerals,
            depth=d,
            use_pruning=True,
        )
        time_prune = (time.perf_counter() - t1) * 1000

        assert tgt_no_prune == tgt_prune

        saved = nodes_no_prune - nodes_prune
        pct = (saved / nodes_no_prune * 100) if nodes_no_prune > 0 else 0.0

        print(f"d = {d} plies{'':<10} | {nodes_no_prune:<12} | {nodes_prune:<12} | {saved:<10} | {pct:>6.1f}%")

    print("=" * 72)


if __name__ == "__main__":
    run_pruning_benchmark()
