import sys
import pathlib

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import (
    Position,
    MineralType,
    INITIAL_BATTERY,
    STEP_BATTERY_COST,
    TRAP_BATTERY_COST,
    MAX_CARGO_CAPACITY,
    DELIVERY_BONUS_PER_ITEM,
)
from core.environment import trap, free
from core.search import astar
from core.logica import coleta_autorizada, fatos_do_jogo
from strategy.minimax import choose_best_target_minimax


class RobotAgent:
    def __init__(self, name: str, base_pos: Position, initial_pos: Position | None = None):
        self.name = name
        self.base = base_pos
        self.pos = initial_pos if initial_pos is not None else base_pos
        self.battery = INITIAL_BATTERY
        self.cargo = 0
        self.score = 0
        self.current_target: Position | None = None
        self.current_path: list[Position] = []
        self.ignored_targets: set[Position] = set()

    def has_battery(self) -> bool:
        return self.battery > 0

    def step(self, env, opponent_pos: Position) -> dict:
        event = {
            "agent": self.name,
            "moved": False,
            "collected": None,
            "delivered": False,
            "battery_cost": 0,
            "current_target": None,
        }

        if self.battery <= 0:
            return event

        available = {p: v for p, v in env.minerals.items() if p not in self.ignored_targets}
        if not available and self.cargo == 0:
            self.current_target = None
            return event

        need_new_target = (
            self.current_target is None
            or (self.current_target != self.base and self.current_target not in env.minerals)
        )

        if need_new_target:
            self.current_path = []

            if self.cargo >= MAX_CARGO_CAPACITY or (not env.minerals and self.cargo > 0):
                self.current_target = self.base
                if self.pos != self.base:
                    path, _, _ = astar(env, self.pos, self.base)
                    self.current_path = path[1:] if path else []
            else:
                while True:
                    available = {p: v for p, v in env.minerals.items() if p not in self.ignored_targets}
                    if not available:
                        if self.cargo > 0:
                            self.current_target = self.base
                            if self.pos != self.base:
                                path, _, _ = astar(env, self.pos, self.base)
                                self.current_path = path[1:] if path else []
                        else:
                            self.current_target = None
                        break

                    target, _ = choose_best_target_minimax(
                        alfa_pos=self.pos,
                        beta_pos=opponent_pos,
                        available_minerals=available,
                        depth=4,
                        alfa_score=self.score,
                        alfa_cargo=self.cargo,
                        ignored_targets=self.ignored_targets,
                        my_base=self.base,
                    )

                    if target is None:
                        self.current_target = None
                        break

                    if target == self.base:
                        self.current_target = self.base
                        if self.pos != self.base:
                            path, _, _ = astar(env, self.pos, self.base)
                            self.current_path = path[1:] if path else []
                        break

                    if target == self.pos:
                        self.current_target = target
                        self.current_path = []
                        break

                    path, cost, _ = astar(env, self.pos, target)
                    if path is None:
                        self.ignored_targets.add(target)
                        continue

                    self.current_target = target
                    self.current_path = path[1:]
                    break

        event["current_target"] = self.current_target

        if self.current_path:
            next_pos = self.current_path.pop(0)
            self.pos = next_pos
            event["moved"] = True

            cost = TRAP_BATTERY_COST if env.grid[next_pos.y][next_pos.x] == trap else STEP_BATTERY_COST
            self.battery = max(0, self.battery - cost)
            event["battery_cost"] = cost

        if self.pos == self.base and self.cargo > 0:
            bonus = self.cargo * DELIVERY_BONUS_PER_ITEM
            self.score += bonus
            self.cargo = 0
            self.battery = INITIAL_BATTERY
            self.ignored_targets.clear()
            self.current_target = None
            self.current_path = []
            event["delivered"] = True

        elif self.pos in env.minerals:
            fatos = fatos_do_jogo(
                env=env,
                pos=self.pos,
                bateria=self.battery,
                carga=self.cargo,
                base=self.base,
            )
            if coleta_autorizada(fatos):
                m_type = env.minerals[self.pos]
                pts = m_type.value
                self.score += pts
                self.cargo += 1
                del env.minerals[self.pos]
                env.grid[self.pos.y][self.pos.x] = free
                event["collected"] = (m_type.name, pts)
                self.current_target = None
                self.current_path = []

        return event
