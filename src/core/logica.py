import sys
import pathlib
from collections import namedtuple

_src_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from core.domain import (
    BATTERY_SECURITY_THRESHOLD,
    MAX_CARGO_CAPACITY,
    STEP_BATTERY_COST,
)

LIMIAR_BATERIA_ALTA = BATTERY_SECURITY_THRESHOLD 
CAPACIDADE_CARGA = MAX_CARGO_CAPACITY              
LIMIAR_BATERIA_BAIXA = 30                          

Regra = namedtuple("Regra", ["nome", "premissas", "conclusao"])


def regra(nome, premissas, conclusao):
    return Regra(nome, frozenset(premissas), conclusao)


BASE_REGRAS = [
    regra("R1", {"B_alta", "nao_C_cheia"}, "P_coleta"),
    regra("R2", {"C_cheia"}, "P_descarga"),
    regra("R3", {"B_insuf_retorno"}, "P_descarga"),
    regra("R4", {"A_adj", "B_baixa"}, "P_rota_alternativa"),
    regra("R5", {"P_descarga", "A_adj"}, "P_rota_alternativa"),
]


def gerar_fatos(bateria, carga, sobre_minerio, armadilha_adjacente, custo_retorno_estimado):
    fatos = set()

    if bateria > LIMIAR_BATERIA_ALTA:
        fatos.add("B_alta")
    if bateria <= LIMIAR_BATERIA_BAIXA:
        fatos.add("B_baixa")
    if bateria < custo_retorno_estimado:
        fatos.add("B_insuf_retorno")

    if carga >= CAPACIDADE_CARGA:
        fatos.add("C_cheia")
    else:
        fatos.add("nao_C_cheia")

    if sobre_minerio:
        fatos.add("S_minerio")
    if armadilha_adjacente:
        fatos.add("A_adj")

    return fatos


def inferir(fatos_observados, base_regras=BASE_REGRAS, rastro=None):
    conhecidos = set(fatos_observados)
    mudou = True

    while mudou:
        mudou = False
        for r in base_regras:
            if r.conclusao not in conhecidos and r.premissas <= conhecidos:
                conhecidos.add(r.conclusao)
                mudou = True
                if rastro is not None:
                    rastro.append((r.nome, r.conclusao))

    return conhecidos - set(fatos_observados)


def coleta_autorizada(fatos_observados, base_regras=BASE_REGRAS):
    if "S_minerio" not in fatos_observados:
        return False
    derivados = inferir(fatos_observados, base_regras)
    return "P_coleta" in derivados and "P_descarga" not in derivados


def fatos_do_jogo(env, pos, bateria, carga, base):
    from core.environment import trap
    from core.search import astar

    armadilha_adjacente = any(
        0 <= n.x < env.width and 0 <= n.y < env.height
        and env.grid[n.y][n.x] == trap
        for n in pos.neighbors()
    )
    _, custo_grafo, _ = astar(env, pos, base)

    return gerar_fatos(
        bateria=bateria,
        carga=carga,
        sobre_minerio=pos in env.minerals,
        armadilha_adjacente=armadilha_adjacente,
        custo_retorno_estimado=custo_grafo * STEP_BATTERY_COST,
    )


def _demonstrar():
    from core.domain import Position
    from core.environment import Environment

    env = Environment(seed=1)
    base = Position(0, 0)
    minerio = next(iter(env.minerals))          

    casos = [
        ("Sobre minério, bateria 60, carga 1", minerio, 60, 1),
        ("Sobre minério, carga 3 (cheia)",     minerio, 60, 3),
        ("Sobre minério, bateria 8, carga 0",  minerio, 8, 0),
        ("Longe do minério, bateria 60",       Position(2, 3), 60, 1),
    ]
    print(f"minério usado: {minerio} ({env.minerals[minerio].name})\n")
    for descricao, pos, bateria, carga in casos:
        fatos = fatos_do_jogo(env, pos, bateria, carga, base)
        rastro = []
        derivados = inferir(fatos, BASE_REGRAS, rastro)
        print(f"Situação : {descricao}")
        print(f"  Fatos observados : {sorted(fatos)}")
        print(f"  Regras disparadas: {[n for n, _ in rastro] or 'nenhuma'}")
        print(f"  Fatos derivados  : {sorted(derivados) or 'nenhum'}")
        print(f"  Coleta autorizada: {coleta_autorizada(fatos)}\n")


if __name__ == "__main__":
    _demonstrar()
