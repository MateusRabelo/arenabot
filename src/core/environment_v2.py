import sys
import random
from core.domain import *

# Identificadores lógicos das células
FREE = "."
WALL = "#"
TRAP = "!"
BASE_A = "A"
BASE_B = "B"

MINERAL_LIST = [
    MineralType.DIAMOND,
    MineralType.RUBY,
    MineralType.GOLD,
    MineralType.SILVER,
    MineralType.COPPER,
]

MINERAL_CHARS = {
    MineralType.DIAMOND: "D",
    MineralType.RUBY: "R",
    MineralType.GOLD: "G",
    MineralType.SILVER: "S",
    MineralType.COPPER: "C",
}

# Cores ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

COLOR_WALL = "\033[38;5;244m"       # Cinza ardósia
COLOR_TRAP = "\033[38;5;196m"       # Vermelho alerta
COLOR_FREE = "\033[38;5;238m"       # Ponto cinza escuro sutil
COLOR_BASE_A = "\033[38;5;46m"      # Verde vibrante
COLOR_BASE_B = "\033[38;5;33m"      # Azul vibrante
COLOR_PATH = "\033[38;5;51m"        # Ciano elétrico
COLOR_TARGET = "\033[38;5;226m\033[1m" # Amarelo ouro brilhante

COLOR_MINERALS = {
    "D": "\033[38;5;81m\033[1m",    # Diamante: Ciano claro brilhante
    "R": "\033[38;5;197m\033[1m",   # Rubi: Vermelho rubi brilhante
    "G": "\033[38;5;220m\033[1m",   # Ouro: Dourado brilhante
    "S": "\033[38;5;253m\033[1m",   # Prata: Branco prateado
    "C": "\033[38;5;172m\033[1m",   # Bronze/Cobre: Laranja bronze
}

if not sys.stdout.isatty():
    RESET = BOLD = DIM = ""
    COLOR_WALL = COLOR_TRAP = COLOR_FREE = COLOR_BASE_A = COLOR_BASE_B = COLOR_PATH = COLOR_TARGET = ""
    COLOR_MINERALS = {k: "" for k in COLOR_MINERALS}


class EnvironmentV2:
    def __init__(self, seed=None, width=ARENA_WIDTH, height=ARENA_HEIGHT, walls=TOTAL_WALLS, traps=TOTAL_TRAPS, minerals=TOTAL_MINERALS):
        self.width = width
        self.height = height
        self.grid = [[FREE] * width for _ in range(height)]
        self.minerals = {}
        self.battery_a = INITIAL_BATTERY
        self.battery_b = INITIAL_BATTERY
        self.seed = seed
        self._generate(seed, walls, traps, minerals)

    def _roll(self, rng):
        x = rng.randint(0, self.width - 1)
        y = rng.randint(0, self.height - 1)
        return Position(x, y)

    def _generate(self, seed, walls, traps, minerals):
        rng = random.Random(seed)

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
            if self.grid[pos.y][pos.x] == FREE:
                self.grid[pos.y][pos.x] = WALL
                placed += 1

        placed = 0
        while placed < traps:
            pos = self._roll(rng)
            if pos in protected:
                continue
            if self.grid[pos.y][pos.x] == FREE:
                self.grid[pos.y][pos.x] = TRAP
                placed += 1

        placed = 0
        while placed < minerals:
            pos = self._roll(rng)
            if pos in protected:
                continue
            if self.grid[pos.y][pos.x] == FREE:
                kind = rng.choice(MINERAL_LIST)
                self.grid[pos.y][pos.x] = MINERAL_CHARS[kind]
                self.minerals[pos] = kind
                placed += 1

    def _format_cell(self, raw_char: str, is_path: bool = False, is_target: bool = False, is_start: bool = False) -> str:
        if is_target:
            return f"{COLOR_TARGET}[{raw_char}]{RESET}"
        if is_start:
            return f"{COLOR_BASE_A}{BOLD}[A]{RESET}"
        if is_path:
            # Se for chão livre ou base vazia, desenha o passo da rota
            if raw_char in (FREE, BASE_A, BASE_B):
                return f"{COLOR_PATH}{BOLD} * {RESET}"
            # Se a rota pisar por cima de um minério ou armadilha, destaca
            return f"{COLOR_PATH}[{raw_char}]{RESET}"

        if raw_char == WALL:
            return f"{COLOR_WALL}███{RESET}"
        if raw_char == TRAP:
            return f"{COLOR_TRAP}{BOLD} ! {RESET}"
        if raw_char == FREE:
            return f"{COLOR_FREE} · {RESET}"
        if raw_char == BASE_A:
            return f"{COLOR_BASE_A}{BOLD} A {RESET}"
        if raw_char == BASE_B:
            return f"{COLOR_BASE_B}{BOLD} B {RESET}"
        if raw_char in COLOR_MINERALS:
            return f"{COLOR_MINERALS[raw_char]} {raw_char} {RESET}"
        return f" {raw_char} "

    def _battery_bar(self, current: int, max_val: int = INITIAL_BATTERY, length: int = 10) -> str:
        pct = max(0, min(100, round((current / max_val) * 100)))
        filled = round((pct / 100) * length)
        empty = length - filled
        color = COLOR_BASE_A if pct > 50 else ("\033[33m" if pct > 20 else COLOR_TRAP)
        bar = f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"
        return f"[{bar}] {pct}%"

    def show(self):
        """Renderiza o mapa com régua de eixos e proporções quadradas."""
        col_header = "     " + " ".join(f"{x:2d}" for x in range(self.width))
        border_top = "    ┌" + "───" * self.width + "┐"
        border_bottom = "    └" + "───" * self.width + "┘"

        print(f"\n{BOLD}ARENA BOT — MAPA DO JOGO{RESET} (Seed: {self.seed})")
        print(f"{DIM}{col_header}{RESET}")
        print(f"{COLOR_WALL}{border_top}{RESET}")

        for y, row in enumerate(self.grid):
            line = "".join(self._format_cell(c) for c in row)
            print(f"{DIM}{y:2d}  {COLOR_WALL}│{RESET}{line}{COLOR_WALL}│{RESET}")

        print(f"{COLOR_WALL}{border_bottom}{RESET}")
        self._print_legend()

    def show_with_path(self, path: list[Position]):
        """Renderiza a grade com destaque elegante do trajeto traçado."""
        if not path:
            self.show()
            return

        start_pos = path[0]
        target_pos = path[-1]
        path_set = set(path[1:-1])

        col_header = "     " + " ".join(f"{x:2d}" for x in range(self.width))
        border_top = "    ┌" + "───" * self.width + "┐"
        border_bottom = "    └" + "───" * self.width + "┘"

        print(f"\n{BOLD}ARENA BOT — NAVEGAÇÃO HEURÍSTICA (A*){RESET} (Seed: {self.seed})")
        print(f"{DIM}{col_header}{RESET}")
        print(f"{COLOR_WALL}{border_top}{RESET}")

        for y, row in enumerate(self.grid):
            cells = []
            for x, c in enumerate(row):
                pos = Position(x, y)
                is_start = (pos == start_pos)
                is_target = (pos == target_pos)
                is_path = (pos in path_set)
                cells.append(self._format_cell(c, is_path=is_path, is_target=is_target, is_start=is_start))

            line = "".join(cells)
            print(f"{DIM}{y:2d}  {COLOR_WALL}│{RESET}{line}{COLOR_WALL}│{RESET}")

        print(f"{COLOR_WALL}{border_bottom}{RESET}")
        self._print_legend()

    def _print_legend(self):
        print(f"\n{BOLD}PAINEL DE TELEMETRIA & LEGENDA:{RESET}")
        print(f"  • Bateria Alfa: {self._battery_bar(self.battery_a)}   • Bateria Beta: {self._battery_bar(self.battery_b)}")
        print(f"  • Minérios Restantes ({len(self.minerals)}): "
              f"{COLOR_MINERALS['D']}D: Diamante (100pts){RESET} | "
              f"{COLOR_MINERALS['R']}R: Rubi (80pts){RESET} | "
              f"{COLOR_MINERALS['G']}G: Ouro (50pts){RESET} | "
              f"{COLOR_MINERALS['S']}S: Prata (30pts){RESET} | "
              f"{COLOR_MINERALS['C']}C: Bronze (10pts){RESET}")
        print(f"  • Elementos: {COLOR_WALL}███ Parede{RESET} | {COLOR_TRAP} ! Armadilha (-4 bat){RESET} | {COLOR_PATH} * Rota A*{RESET} | {COLOR_TARGET}[X] Alvo Selecionado{RESET}\n")
