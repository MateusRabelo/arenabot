import sys
import pathlib
import statistics
import time

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.game import Match


def run_tournament(start_seed: int = 1, end_seed: int = 30):
    alfa_wins = 0
    beta_wins = 0
    draws = 0

    alfa_scores = []
    beta_scores = []
    all_scores = []
    match_turns = []

    print("=" * 80)
    print("TORNEIO OFICIAL DO ARENA BOT")
    print("=" * 80)
    print(f"{'Seed':<6} | {'Vencedor':<10} | {'Alfa Pts':<10} | {'Beta Pts':<10} | {'Turnos':<8} | {'Motivo do Fim'}")
    print("-" * 80)

    t0 = time.perf_counter()

    for seed in range(start_seed, end_seed + 1):
        match = Match(seed=seed, max_turns=600)
        res = match.run_all()

        winner = res["winner"]
        if winner == "Alfa":
            alfa_wins += 1
        elif winner == "Beta":
            beta_wins += 1
        else:
            draws += 1

        alfa_scores.append(res["alfa_score"])
        beta_scores.append(res["beta_score"])
        all_scores.extend([res["alfa_score"], res["beta_score"]])
        match_turns.append(res["turns"])

        print(
            f"{seed:<6} | {winner:<10} | {res['alfa_score']:<10} | {res['beta_score']:<10} | {res['turns']:<8} | {res['reason']}",
            flush=True,
        )

    total_time = time.perf_counter() - t0
    total_matches = end_seed - start_seed + 1

    avg_score_alfa = statistics.mean(alfa_scores)
    stdev_score_alfa = statistics.stdev(alfa_scores) if total_matches > 1 else 0.0

    avg_score_beta = statistics.mean(beta_scores)
    stdev_score_beta = statistics.stdev(beta_scores) if total_matches > 1 else 0.0

    avg_turns = statistics.mean(match_turns)
    stdev_turns = statistics.stdev(match_turns) if total_matches > 1 else 0.0

    print("=" * 80)
    print("RESUMO E ESTATISTICAS")
    print("=" * 80)
    print(f"Total de Partidas          : {total_matches}")
    print(f"Vitórias de Alfa           : {alfa_wins} ({(alfa_wins / total_matches) * 100:.1f}%)")
    print(f"Vitórias de Beta           : {beta_wins} ({(beta_wins / total_matches) * 100:.1f}%)")
    print(f"Empates                    : {draws} ({(draws / total_matches) * 100:.1f}%)")
    print("-" * 80)
    print(f"Pontuação Média de Alfa    : {avg_score_alfa:.2f} (Desvio Padrão: {stdev_score_alfa:.2f})")
    print(f"Pontuação Média de Beta    : {avg_score_beta:.2f} (Desvio Padrão: {stdev_score_beta:.2f})")
    print(f"Duração Média em Turnos    : {avg_turns:.2f} (Desvio Padrão: {stdev_turns:.2f})")
    print(f"Tempo Total do Torneio     : {total_time:.2f} segundos")
    print("=" * 80)


if __name__ == "__main__":
    run_tournament(start_seed=1, end_seed=30)
