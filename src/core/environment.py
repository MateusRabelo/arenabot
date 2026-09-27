import random
from core.domain import *

free = "."
wall = "#"
trap = "!"
BASE_A = "A"
BASE_B = "B"

minerals_list = [
    MineralType.DIAMOND,
    MineralType.RUBY,
    MineralType.GOLD,
    MineralType.SILVER,
    MineralType.COPPER,
]

char_minerais = {
    MineralType.DIAMOND: "D",
    MineralType.RUBY: "R",
    MineralType.GOLD: "G",
    MineralType.SILVER: "S",
    MineralType.COPPER: "C",
}


class Environment:
    def __init__(self, seed=None, width=ARENA_WIDTH, height=ARENA_HEIGHT, walls=TOTAL_WALLS, traps=TOTAL_TRAPS, minerals=TOTAL_MINERALS):
        self.width = width
        self.height = height
        self.grid = [[free] * width for _ in range(height)]
        self.minerals = {}
        self._generate(seed, walls, traps, minerals)

    def _sorteio(self, rng):
        x = rng.randint(0, self.width - 1)
        y = rng.randint(0, self.height - 1)
        return Position(x, y)

    def _generate(self, seed, walls, traps, minerals):
        rng = random.Random(seed)

        x, y = ALFA_BASE
        self.grid[y][x] = BASE_A
        x, y = BETA_BASE
        self.grid[y][x] = BASE_B

        placed = 0
        while placed < walls:
            pos = self._sorteio(rng)
            if self.grid[pos.y][pos.x] == free:
                self.grid[pos.y][pos.x] = wall
                placed += 1

        placed = 0
        while placed < traps:
            pos = self._sorteio(rng)
            if self.grid[pos.y][pos.x] == free:
                self.grid[pos.y][pos.x] = trap
                placed += 1

        placed = 0
        while placed < minerals:
            pos = self._sorteio(rng)
            if self.grid[pos.y][pos.x] == free:
                tipo = rng.choice(minerals_list)
                self.grid[pos.y][pos.x] = char_minerais[tipo]
                self.minerals[pos] = tipo
                placed += 1

    def show(self):
        borda = wall * (self.width + 2)
        print(borda)
        for linha in self.grid:
            print(wall + "".join(linha) + wall)
        print(borda)
