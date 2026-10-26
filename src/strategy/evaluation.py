import sys
import pathlib

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import Position, MineralType

DEFAULT_OMEGA: float = 2.5


def evaluate_target(
    alfa_pos: Position,
    beta_pos: Position,
    mineral_pos: Position,
    mineral_value: int,
    omega: float = DEFAULT_OMEGA,
) -> float:
    dist_alfa = alfa_pos.manhattan_distance(mineral_pos)
    dist_beta = beta_pos.manhattan_distance(mineral_pos)
    spatial_advantage = dist_beta - dist_alfa
    return mineral_value + (omega * spatial_advantage)


def rank_available_minerals(
    alfa_pos: Position,
    beta_pos: Position,
    available_minerals: dict[Position, MineralType],
    omega: float = DEFAULT_OMEGA,
    ignored_targets: set[Position] | None = None,
) -> list[tuple[Position, MineralType, float]]:
    if ignored_targets is None:
        ignored_targets = set()

    ranked = []
    for pos, m_type in available_minerals.items():
        if pos in ignored_targets:
            continue

        score = evaluate_target(
            alfa_pos=alfa_pos,
            beta_pos=beta_pos,
            mineral_pos=pos,
            mineral_value=m_type.value,
            omega=omega,
        )
        ranked.append((pos, m_type, score))

    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked

