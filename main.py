import sys
import os
import time
import random
import argparse
import pathlib

_src_dir = str(pathlib.Path(__file__).resolve().parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.game import Match
from views.terminal_view import render_board, BOLD, RESET


def run_interactive_match(seed: int = 1, delay: float = 0.6, max_turns: int = 600, clear: bool = True, debug: bool = False):
    match = Match(seed=seed, max_turns=max_turns)
    last_event = None

    if clear and sys.stdout.isatty():
        sys.stdout.write("\033[H\033[J")
    print(render_board(match, last_event=last_event, clear_screen=clear, debug=debug))

    time.sleep(delay if delay > 0 else 0)

    while not match.is_finished():
        last_event = match.step_turn()
        if delay > 0:
            frame = render_board(match, last_event=last_event, clear_screen=clear, debug=debug)
            print(frame)

            time.sleep(delay)

    final_frame = render_board(match, last_event=last_event, clear_screen=clear, debug=debug)
    print(final_frame)
    print("")
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}PARTIDA ENCERRADA!{RESET}")
    print(f"Vencedor : {BOLD}{match.winner}{RESET}")
    print(f"Placar   : Alfa {BOLD}{match.alfa.score}{RESET} x {BOLD}{match.beta.score}{RESET} Beta")
    print(f"Duração  : {match.turns} turnos")
    print(f"Motivo   : {match.reason}")
    print(f"{BOLD}{'=' * 60}{RESET}")


def run_tournament():
    from experiments.tournament import run_tournament as execute_tourney
    execute_tourney(start_seed=1, end_seed=30)


def run_benchmarks():
    from experiments.search_benchmark import run_search_benchmark
    run_search_benchmark(num_seeds=10)

    print("")

    from experiments.pruning_benchmark import run_pruning_benchmark
    run_pruning_benchmark()


def main():
    parser = argparse.ArgumentParser(description="Arena Bot 00000010")
    parser.add_argument("--tournament", action="store_true", help="Executa o torneio oficial de 30 partidas (sementes 1 a 30)")
    parser.add_argument("--benchmark", action="store_true", help="Executa os benchmarks de navegação (A* vs BFS) e poda alfa-beta")
    parser.add_argument("--debug", action="store_true", help="Exibe caminhos traçados e os algoritmos de decisão")

    args = parser.parse_args()

    if args.tournament:
        run_tournament()
    elif args.benchmark:
        run_benchmarks()
    else:
        run_interactive_match(seed=random.randint(1, 999999), debug=args.debug)


if __name__ == "__main__":
    main()
