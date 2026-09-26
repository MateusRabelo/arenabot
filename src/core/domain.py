from dataclasses import dataclass # pra um melhor controle da lista grid do jog
from enum import Enum


#infos da tabela 1 e 2
ARENA_WIDTH = 15
ARENA_HEIGHT = 9

TOTAL_WALLS = 25
TOTAL_TRAPS = 6
TOTAL_MINERALS = 12

INITIAL_BATTERY = 100
STEP_BATTERY_COST = 2
TRAP_BATTERY_COST = 4

GRAPH_COST_NORMAL = 1
GRAPH_COST_TRAP = 2

MAX_CARGO_CAPACITY = 3
DELIVERY_BONUS_PER_ITEM = 10
BATTERY_SECURITY_THRESHOLD = 10

ALFA_BASE = (0, 0)
BETA_BASE = (ARENA_WIDTH -1, ARENA_HEIGHT -1)



@dataclass(frozen = True)
class Position:
    x: int
    y: int

    def manhattan_distance(self, other_pos) -> int:
        return abs(self.x - other_pos.x) + abs(self.y - other_pos.y)


    def neighbors(self) -> list['Position']:
        return [
            Position(self.x, self.y -1),  #up
            Position(self.x, self.y + 1),  #down
            Position(self.x - 1, self.y),  #left
            Position(self.x + 1, self.y),  #right
        ]        

    

class MineralType(Enum):
    DDIAMOND = 100
    RUBy = 80
    GOLD = 50
    SILVER = 30
    COPPER = 10

    def get_points(self) -> int:
        return self.value

