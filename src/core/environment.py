import sys
import random
from core.domain import *

free = "."
wall = "#"
trap = "!"
path_char = "*"
BASE_A = "A"
BASE_B = "B"

mineral_list = [
    MineralType.DIAMOND,
    MineralType.RUBY,
    MineralType.GOLD,
    MineralType.SILVER,
    MineralType.COPPER,
]

mineral_chars = {
    MineralType.DIAMOND: "D",
    MineralType.RUBY: "R",
    MineralType.GOLD: "G",
    MineralType.SILVER: "S",
    MineralType.COPPER: "C",
}

reset = "\033[0m"

colors = {
    free: "\033[90m",
    wall: "\033[37m",
    trap: "\033[1;31m",
    path_char: "\033[96m",
    BASE_A: "\033[32m",
    BASE_B: "\033[34m",
    "D": "\033[97m",
    "R": "\033[91m",
    "G": "\033[93m",
    "S": "\033[37m",
    "C": "\033[33m",
}

if not sys.stdout.isatty():
    colors = {}
    reset = ""


class Environment:
    def __init__(self, seed=None, width=ARENA_WIDTH, height=ARENA_HEIGHT, walls=TOTAL_WALLS, traps=TOTAL_TRAPS, minerals=TOTAL_MINERALS):
        self.width = width
        self.height = height
        self.grid = [[free] * width for _ in range(height)]
        self.minerals = {}
        self.battery_a = INITIAL_BATTERY
        self.battery_b = INITIAL_BATTERY
        self._generate(seed, walls, traps, minerals)

    def _roll(self, rng):
        x = rng.randint(0, self.width - 1)
        y = rng.randint(0, self.height - 1)
        return Position(x, y)

    def _generate(self, seed, walls, traps, minerals):
        rng = random.Random(seed)

        #precisa virar Position, senao a comparacao com tupla da False e a protecao nao vale
        protected = [Position(x, y) for x, y in ALFA_BASE + BETA_BASE]

        for x, y in ALFA_BASE:
            self.grid[y][x] = BASE_A
        for x, y in BETA_BASE:
            self.grid[y][x] = BASE_B

        placed = 0
        while placed < walls:
            pos = self._roll(rng)
            if pos in protected:
                continue
            if self.grid[pos.y][pos.x] == free:
                self.grid[pos.y][pos.x] = wall
                placed += 1

        placed = 0
        while placed < traps:
            pos = self._roll(rng)
            if pos in protected:
                continue
            if self.grid[pos.y][pos.x] == free:
                self.grid[pos.y][pos.x] = trap
                placed += 1

        placed = 0
        while placed < minerals:
            pos = self._roll(rng)
            if pos in protected:
                continue
            if self.grid[pos.y][pos.x] == free:
                kind = rng.choice(mineral_list)
                self.grid[pos.y][pos.x] = mineral_chars[kind]
                self.minerals[pos] = kind
                placed += 1

    def _percentage(self, battery):
        return round(battery / INITIAL_BATTERY * 100)

    def _colorize(self, text):
        return "".join(f"{colors[c]}{c}{reset}" if c in colors else c for c in text)

    def show(self):
        border = wall * (self.width + 2)
        print(self._colorize(border))
        for row in self.grid:
            print(self._colorize(wall + "".join(row) + wall))
        print(self._colorize(border))
        print(self._colorize(wall) + f" Minerais: {len(self.minerals)}")
        print(self._colorize(wall) + f" Bateria A: {self._percentage(self.battery_a)}%")
        print(self._colorize(wall) + f" Bateria B: {self._percentage(self.battery_b)}%")

    def show_with_path(self, path):
        gap = "   "
        border = wall * (self.width + 2)
        marked = {(pos.x, pos.y) for pos in path}

        print("ORIGINAL".center(self.width + 2) + gap + "COM CAMINHO".center(self.width + 2))
        print(self._colorize(border) + gap + self._colorize(border))
        for y, row in enumerate(self.grid):
            left = wall + "".join(row) + wall
            right = wall + "".join(path_char if (x, y) in marked else c for x, c in enumerate(row)) + wall
            print(self._colorize(left) + gap + self._colorize(right))
        print(self._colorize(border) + gap + self._colorize(border))
        print(self._colorize(wall) + f" Minerais: {len(self.minerals)}")
        print(self._colorize(wall) + f" Bateria A: {self._percentage(self.battery_a)}%")
        print(self._colorize(wall) + f" Bateria B: {self._percentage(self.battery_b)}%")
