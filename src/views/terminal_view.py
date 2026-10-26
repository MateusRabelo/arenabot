import sys
import os
from core.domain import Position, ALFA_BASE, BETA_BASE, MineralType

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

COLOR_WALL = "\033[38;5;244m"
COLOR_TRAP = "\033[38;5;196m"
COLOR_FREE = "\033[38;5;238m"
COLOR_ALFA = "\033[38;5;81m\033[1m"
COLOR_BETA = "\033[38;5;203m\033[1m"
COLOR_BASE_A = "\033[38;5;46m"
COLOR_BASE_B = "\033[38;5;33m"

MINERAL_COLORS = {
    MineralType.DIAMOND: ("\033[38;5;81m\033[1m", "D"),
    MineralType.RUBY: ("\033[38;5;197m\033[1m", "R"),
    MineralType.GOLD: ("\033[38;5;220m\033[1m", "G"),
    MineralType.SILVER: ("\033[38;5;253m\033[1m", "S"),
    MineralType.COPPER: ("\033[38;5;172m\033[1m", "C"),
}


def battery_bar(val: int, length: int = 10) -> str:
    pct = max(0, min(100, val))
    filled = round((pct / 100) * length)
    empty = length - filled
    color = COLOR_BASE_A if pct > 50 else ("\033[33m" if pct > 20 else COLOR_TRAP)
    return f"[{color}{'█' * filled}{DIM}{'░' * empty}{RESET}] {pct:3d}%"


def render_board(match, last_event=None, clear_screen: bool = True):
    if clear_screen and sys.stdout.isatty():
        sys.stdout.write("\033[H\033[J")

    env = match.env
    alfa_p = match.alfa.pos
    beta_p = match.beta.pos
    base_a = Position(*ALFA_BASE[0])
    base_b = Position(*BETA_BASE[1])

    from core.environment import wall, trap

    lines = []
    lines.append(f"{BOLD}ARENA BOT — SISTEMA COMPETITIVO DE COLETA (PP01){RESET}")
    lines.append(f"Turno: {BOLD}{match.turns}{RESET} | Semente: {BOLD}{match.seed}{RESET} | Minérios restantes: {BOLD}{len(env.minerals)}{RESET}")
    lines.append("")

    col_header = "     " + " ".join(f"{x:2d}" for x in range(env.width))
    lines.append(f"{DIM}{col_header}{RESET}")
    lines.append(f"{COLOR_WALL}    ┌{'───' * env.width}┐{RESET}")

    for y in range(env.height):
        row_str = []
        for x in range(env.width):
            pos = Position(x, y)
            if pos == alfa_p and pos == beta_p:
                row_str.append(f"{COLOR_ALFA}A{COLOR_BETA}B{RESET} ")
            elif pos == alfa_p:
                row_str.append(f"{COLOR_ALFA}[A]{RESET}")
            elif pos == beta_p:
                row_str.append(f"{COLOR_BETA}[B]{RESET}")
            elif pos in env.minerals:
                color, char = MINERAL_COLORS[env.minerals[pos]]
                row_str.append(f"{color} {char} {RESET}")
            elif env.grid[y][x] == wall:
                row_str.append(f"{COLOR_WALL}███{RESET}")
            elif env.grid[y][x] == trap:
                row_str.append(f"{COLOR_TRAP}{BOLD} ! {RESET}")
            elif pos == base_a:
                row_str.append(f"{COLOR_BASE_A}{BOLD}⌂A {RESET}")
            elif pos == base_b:
                row_str.append(f"{COLOR_BASE_B}{BOLD}⌂B {RESET}")
            else:
                row_str.append(f"{COLOR_FREE} · {RESET}")

        lines.append(f"{DIM}{y:2d}  {COLOR_WALL}│{RESET}{''.join(row_str)}{COLOR_WALL}│{RESET}")

    lines.append(f"{COLOR_WALL}    └{'───' * env.width}┘{RESET}")
    lines.append("")

    lines.append(f"{BOLD}TELEMETRIA DOS AGENTES:{RESET}")
    alfa_tgt = match.alfa.current_target
    beta_tgt = match.beta.current_target
    lines.append(
        f"  {COLOR_ALFA}Alfa (Azul){RESET}  : Pontos: {BOLD}{match.alfa.score:4d}{RESET} | "
        f"Bateria: {battery_bar(match.alfa.battery)} | "
        f"Carga: {match.alfa.cargo}/3 | "
        f"Alvo: {alfa_tgt}"
    )
    lines.append(
        f"  {COLOR_BETA}Beta (Verm){RESET}  : Pontos: {BOLD}{match.beta.score:4d}{RESET} | "
        f"Bateria: {battery_bar(match.beta.battery)} | "
        f"Carga: {match.beta.cargo}/3 | "
        f"Alvo: {beta_tgt}"
    )

    if last_event:
        agent = last_event.get("agent", "")
        color = COLOR_ALFA if agent == "Alfa" else COLOR_BETA
        details = []
        if last_event.get("collected"):
            m = last_event["collected"]
            if isinstance(m, (tuple, list)):
                m_name, m_val = m[0], m[1]
            else:
                m_name = getattr(m, "name", str(m))
                m_val = getattr(m, "value", "")
            details.append(f"Coletou {m_name} (+{m_val} pts) [Validação Lógica: P_coleta autorizado]")
        if last_event.get("delivered"):
            details.append("Entregou carga na base (+bônus, recarga 100%)")
        if last_event.get("moved"):
            details.append(f"Moveu (-{last_event.get('battery_cost', 0)} bat)")
        lines.append(f"  {BOLD}Último Evento:{RESET} {color}{agent}{RESET}: {' | '.join(details) if details else 'Aguardando'}")

    return "\n".join(lines)
