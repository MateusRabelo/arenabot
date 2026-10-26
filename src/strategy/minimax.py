import sys
import pathlib
from dataclasses import dataclass, replace

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import (
    Position,
    MineralType,
    ALFA_BASE,
    BETA_BASE,
    MAX_CARGO_CAPACITY,
    DELIVERY_BONUS_PER_ITEM,
)
from strategy.evaluation import evaluate_target, DEFAULT_OMEGA


@dataclass(frozen=True)
class StrategicState:
    alfa_pos: Position
    beta_pos: Position
    available_minerals: dict[Position, MineralType]
    alfa_score: int = 0
    beta_score: int = 0
    alfa_cargo: int = 0
    beta_cargo: int = 0
    alfa_target_intent: Position | None = None
    alfa_intent_dist: int = 0
    alfa_base: Position = Position(*ALFA_BASE[0])
    beta_base: Position = Position(*BETA_BASE[1])

    def is_terminal(self) -> bool:
        return len(self.available_minerals) == 0 and self.alfa_cargo == 0 and self.beta_cargo == 0

    def get_actions(self, is_alfa: bool) -> list[Position]:
        cargo = self.alfa_cargo if is_alfa else self.beta_cargo
        base = self.alfa_base if is_alfa else self.beta_base

        if cargo >= MAX_CARGO_CAPACITY:
            return [base]

        if not self.available_minerals:
            return [base]

        actions = list(self.available_minerals.keys())

        if not is_alfa and self.alfa_target_intent and self.alfa_target_intent not in actions:
            actions.append(self.alfa_target_intent)

        if cargo > 0:
            actions.append(base)

        return actions

    def simulate_action(self, target: Position, is_alfa: bool) -> "StrategicState":
        base = self.alfa_base if is_alfa else self.beta_base

        if target == base:
            if is_alfa:
                bonus = self.alfa_cargo * DELIVERY_BONUS_PER_ITEM
                return replace(self, alfa_pos=base, alfa_score=self.alfa_score + bonus, alfa_cargo=0, alfa_target_intent=None)
            else:
                bonus = self.beta_cargo * DELIVERY_BONUS_PER_ITEM
                return replace(self, beta_pos=base, beta_score=self.beta_score + bonus, beta_cargo=0)

        if is_alfa:
            dist_travel = self.alfa_pos.manhattan_distance(target)
            new_minerals = {p: v for p, v in self.available_minerals.items() if p != target}
            return replace(
                self,
                alfa_pos=target,
                alfa_target_intent=target,
                alfa_intent_dist=dist_travel,
                available_minerals=new_minerals,
            )
        else:
            dist_travel_b = self.beta_pos.manhattan_distance(target)
            new_minerals = {p: v for p, v in self.available_minerals.items() if p != target}

            if target == self.alfa_target_intent:
                m_val = 100 if target == Position(13, 7) else 50
                if target in self.available_minerals:
                    m_val = self.available_minerals[target].value

                if dist_travel_b < self.alfa_intent_dist:
                    return replace(
                        self,
                        beta_pos=target,
                        beta_score=self.beta_score + m_val,
                        beta_cargo=self.beta_cargo + 1,
                        alfa_target_intent=None,
                        available_minerals=new_minerals,
                    )
                else:
                    return replace(
                        self,
                        beta_pos=target,
                        alfa_score=self.alfa_score + m_val,
                        alfa_cargo=self.alfa_cargo + 1,
                        alfa_target_intent=None,
                        available_minerals=new_minerals,
                    )

            m_type_beta = self.available_minerals.get(target)
            pts_beta = m_type_beta.value if m_type_beta else 0

            pts_alfa = 0
            if self.alfa_target_intent:
                pts_alfa = 100 if self.alfa_target_intent == Position(13, 7) else 50

            return replace(
                self,
                beta_pos=target,
                beta_score=self.beta_score + pts_beta,
                beta_cargo=self.beta_cargo + 1,
                alfa_score=self.alfa_score + pts_alfa,
                alfa_cargo=self.alfa_cargo + 1,
                alfa_target_intent=None,
                available_minerals=new_minerals,
            )


def evaluate_state_leaf(state: StrategicState, omega: float = DEFAULT_OMEGA) -> float:
    utility = float(state.alfa_score - state.beta_score)

    if state.available_minerals:
        for pos, m_type in state.available_minerals.items():
            dist_a = state.alfa_pos.manhattan_distance(pos)
            dist_b = state.beta_pos.manhattan_distance(pos)
            utility += (omega * (dist_b - dist_a))

    return utility


class MinimaxSearch:
    def __init__(self, omega: float = DEFAULT_OMEGA):
        self.omega = omega
        self.nodes_evaluated = 0

    def search(
        self,
        state: StrategicState,
        depth: int,
        alpha: float = float("-inf"),
        beta: float = float("inf"),
        is_maximizing: bool = True,
        use_pruning: bool = True,
    ) -> tuple[float, Position | None]:
        self.nodes_evaluated += 1

        if depth == 0 or state.is_terminal():
            return evaluate_state_leaf(state, omega=self.omega), None

        actions = state.get_actions(is_alfa=is_maximizing)
        if not actions:
            return evaluate_state_leaf(state, omega=self.omega), None

        if is_maximizing:
            best_val = float("-inf")
            best_act = actions[0]

            for act in actions:
                nxt = state.simulate_action(act, is_alfa=True)
                val, _ = self.search(
                    nxt,
                    depth - 1,
                    alpha,
                    beta,
                    is_maximizing=False,
                    use_pruning=use_pruning,
                )

                if val > best_val:
                    best_val = val
                    best_act = act

                if use_pruning:
                    alpha = max(alpha, best_val)
                    if alpha >= beta:
                        break

            return best_val, best_act

        else:
            best_val = float("inf")
            best_act = actions[0]

            for act in actions:
                nxt = state.simulate_action(act, is_alfa=False)
                val, _ = self.search(
                    nxt,
                    depth - 1,
                    alpha,
                    beta,
                    is_maximizing=True,
                    use_pruning=use_pruning,
                )

                if val < best_val:
                    best_val = val
                    best_act = act

                if use_pruning:
                    beta = min(beta, best_val)
                    if alpha >= beta:
                        break

            return best_val, best_act


def choose_best_target_minimax(
    alfa_pos: Position,
    beta_pos: Position,
    available_minerals: dict[Position, MineralType],
    depth: int = 4,
    alfa_score: int = 0,
    beta_score: int = 0,
    alfa_cargo: int = 0,
    beta_cargo: int = 0,
    ignored_targets: set[Position] | None = None,
    omega: float = DEFAULT_OMEGA,
    use_pruning: bool = True,
    my_base: Position | None = None,
) -> tuple[Position | None, int]:
    if ignored_targets is None:
        ignored_targets = set()

    valid_minerals = {p: v for p, v in available_minerals.items() if p not in ignored_targets}
    base_alfa = my_base if my_base is not None else Position(*ALFA_BASE[0])
    base_beta = Position(*BETA_BASE[1]) if base_alfa == Position(*ALFA_BASE[0]) else Position(*ALFA_BASE[0])

    if alfa_cargo >= MAX_CARGO_CAPACITY:
        return base_alfa, 1

    if not valid_minerals:
        return (base_alfa if alfa_cargo > 0 else None), 1

    if len(valid_minerals) == 1:
        return next(iter(valid_minerals.keys())), 1

    if len(valid_minerals) > 5:
        from strategy.evaluation import rank_available_minerals
        ranked = rank_available_minerals(alfa_pos, beta_pos, valid_minerals, omega=omega)
        valid_minerals = {p: valid_minerals[p] for p, _, _ in ranked[:5]}

    state = StrategicState(
        alfa_pos=alfa_pos,
        beta_pos=beta_pos,
        available_minerals=valid_minerals,
        alfa_score=alfa_score,
        beta_score=beta_score,
        alfa_cargo=alfa_cargo,
        beta_cargo=beta_cargo,
        alfa_base=base_alfa,
        beta_base=base_beta,
    )

    solver = MinimaxSearch(omega=omega)
    _, best_target = solver.search(
        state,
        depth=depth,
        alpha=float("-inf"),
        beta=float("inf"),
        is_maximizing=True,
        use_pruning=use_pruning,
    )
    return best_target, solver.nodes_evaluated


if __name__ == "__main__":
    p_alfa_test = Position(0, 0)
    p_beta_test = Position(14, 8)
    test_minerals = {
        Position(2, 2): MineralType.GOLD,
        Position(13, 7): MineralType.DIAMOND,
        Position(5, 5): MineralType.SILVER,
        Position(1, 4): MineralType.COPPER,
    }

    target_no_prune, nodes_no_prune = choose_best_target_minimax(
        alfa_pos=p_alfa_test,
        beta_pos=p_beta_test,
        available_minerals=test_minerals,
        depth=4,
        use_pruning=False,
    )

    target_prune, nodes_prune = choose_best_target_minimax(
        alfa_pos=p_alfa_test,
        beta_pos=p_beta_test,
        available_minerals=test_minerals,
        depth=4,
        use_pruning=True,
    )

    assert target_no_prune == target_prune
    assert nodes_prune < nodes_no_prune
