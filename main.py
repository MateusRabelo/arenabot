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


def run_interactive_match(seed: int = 1, delay: float = 0.08, max_turns: int = 600, clear: bool = True):
    match = Match(seed=seed, max_turns=max_turns)
    last_event = None

    if clear and sys.stdout.isatty():
        sys.stdout.write("\033[H\033[J")
    print(render_board(match, last_event=last_event, clear_screen=clear))

    time.sleep(delay if delay > 0 else 0)

    while not match.is_finished():
        last_event = match.step_turn()
        if delay > 0:
            frame = render_board(match, last_event=last_event, clear_screen=clear)
            print(frame)
            
            time.sleep(delay)

    final_frame = render_board(match, last_event=last_event, clear_screen=clear)
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
    parser = argparse.ArgumentParser(description="Arena Bot — Sistema Competitivo de Coleta (PP01)")
    parser.add_argument("--seed", type=int, default=None, help="Semente do gerador de mapa (aleatória se omitida)")
    parser.add_argument("--delay", type=float, default=0.06, help="Tempo em segundos entre cada turno (padrão: 0.06; use 0 para instantâneo)")
    parser.add_argument("--max-turns", type=int, default=600, help="Limite máximo de turnos da partida (padrão: 600)")
    parser.add_argument("--no-clear", action="store_true", help="Não limpar o terminal entre turnos")
    parser.add_argument("--tournament", action="store_true", help="Executa o torneio oficial de 30 partidas (sementes 1 a 30)")
    parser.add_argument("--benchmark", action="store_true", help="Executa os benchmarks de navegação (A* vs BFS) e poda alfa-beta")

    args = parser.parse_args()

    if args.tournament:
        run_tournament()
    elif args.benchmark:
        run_benchmarks()
    else:
        chosen_seed = random.randint(1, 999999) if args.seed is None else args.seed
        run_interactive_match(
            seed=chosen_seed,
            delay=args.delay,
            max_turns=args.max_turns,
            clear=not args.no_clear,
        )


if __name__ == "__main__":
    main()
