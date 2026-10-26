import sys
import pathlib

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import Position, ALFA_BASE, BETA_BASE
from core.environment import Environment
from core.agent import RobotAgent


class Match:
    def __init__(self, seed: int = 1, max_turns: int = 1000):
        self.seed = seed
        self.max_turns = max_turns
        self.env = Environment(seed=seed)
        self.alfa = RobotAgent(name="Alfa", base_pos=Position(*ALFA_BASE[0]))
        self.beta = RobotAgent(name="Beta", base_pos=Position(*BETA_BASE[1]))
        self.turns = 0
        self.finished = False
        self.winner = None
        self.reason = ""

    def is_finished(self) -> bool:
        if self.finished:
            return True

        if self.turns >= self.max_turns:
            self.finished = True
            self.reason = "Limite maximo de turnos atingido"
            self._determine_winner()
            return True

        if self.alfa.battery <= 0 and self.beta.battery <= 0:
            self.finished = True
            self.reason = "Ambos os robos esgotaram a bateria"
            self._determine_winner()
            return True

        minerals_left = len(self.env.minerals)
        cargo_left = self.alfa.cargo + self.beta.cargo
        if minerals_left == 0 and cargo_left == 0:
            self.finished = True
            self.reason = "Todos os minerios foram coletados e entregues"
            self._determine_winner()
            return True

        alfa_has_work = self.alfa.cargo > 0 or any(p not in self.alfa.ignored_targets for p in self.env.minerals)
        beta_has_work = self.beta.cargo > 0 or any(p not in self.beta.ignored_targets for p in self.env.minerals)
        if not alfa_has_work and not beta_has_work:
            self.finished = True
            self.reason = "Nao restam minerios alcancaveis"
            self._determine_winner()
            return True

        return False

    def _determine_winner(self):
        if self.alfa.score > self.beta.score:
            self.winner = "Alfa"
        elif self.beta.score > self.alfa.score:
            self.winner = "Beta"
        else:
            self.winner = "Empate"

    def step_turn(self) -> dict:
        if self.is_finished():
            return {"finished": True, "winner": self.winner, "reason": self.reason}

        self.turns += 1

        if self.turns % 2 == 1:
            active_agent = self.alfa
            opponent_pos = self.beta.pos
        else:
            active_agent = self.beta
            opponent_pos = self.alfa.pos

        if active_agent.battery <= 0:
            return {
                "turn": self.turns,
                "agent": active_agent.name,
                "skipped": True,
                "reason": "Sem bateria",
            }

        event = active_agent.step(self.env, opponent_pos)
        event["turn"] = self.turns

        self.is_finished()
        return event

    def run_all(self) -> dict:
        while not self.is_finished():
            self.step_turn()

        return {
            "seed": self.seed,
            "turns": self.turns,
            "winner": self.winner,
            "alfa_score": self.alfa.score,
            "beta_score": self.beta.score,
            "reason": self.reason,
            "minerals_remaining": len(self.env.minerals),
        }


if __name__ == "__main__":
    match = Match(seed=1)
    res = match.run_all()
    assert res["winner"] in ("Alfa", "Beta", "Empate")
    assert res["turns"] > 0
