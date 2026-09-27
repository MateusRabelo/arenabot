# ArenaBot — branch `astar`

Navegação do ArenaBot: geração da arena + **A\*** para pathfinding, com **BFS** de referência.

Esta branch entrega **a rota, não o jogo**. Ela so faz como chegar no alvo.


- **Trocar o alvo**: `main.py:15` — `goal = list(env.minerals)[5]` (índice 0 a 11).
- **Trocar a arena**: mude o `seed` em `main.py:11`. Mesma seed, mesma arena.

---

## O que ele faz

| Arquivo | O que faz |
|---|---|
| `src/core/environment.py` | Fiz para imprimir a arena e gerar ela bonitinha para nos |
| `src/core/search.py` | aqui é o A\* e tem um BFS para comparação que o professor pediu. |
| `main.py` | Escolhe a arena, o alvo, chama a busca e imprime. |

O `search` recebe o ambiente `Environment` e lê o grid por caractere: `#` é parede (não entra no grafo), `!`
é armadilha (que tem os custos) e todo o resto é chão, ele não considera os mineral.

O custo é lido do **destino**, então `c(n, n') ≠ c(n', n)` e é isso que
faz o robô contornar a armadilha em vez de atravessar. A heurística é a **Manhattan** que tem no projeto dele.
## O contrato

```python
path, cost, expanded = astar(env, start, goal)      # (None, inf, n) se inalcançável
results = compare(env, start, goal)                 # A* e BFS, com custo/nós/tempo
```

O caminho é uma lista de `Position` começando em `start` e terminando em `goal`, então
`len(path) - 1` é o número de passos e para andar um passo use `path[1]`, e não a lista inteira.
`inf` é `float("inf")` — trate o `None` antes de olhar o custo.

Auxiliares: `is_walkable` (use antes de indexar o grid), `walkable_neighbors` (4-vizinhos),
`step_cost` (custo de entrar), `rebuild_path`.

`env.minerals` é um `dict` indexado por `Position`, com valores `MineralType` (100/80/50/30/10).
`get_points()` existe e **ninguém chama** é a porta de entrada para a escolha de alvo.

---

## O que precisa fazer em cima

1. **O ciclo de turno.** Nada executa turno hoje. Depois do `astar`, use `path[1]` para andar **um
   passo por turno** e descontar a bateria — o `path` é o plano, não a ação.
2. **O robô.** Não existe agente, carga, pontuação nem quem escolhe a vez.
3. **A escolha de alvo** (Minimax com poda alfa-beta). Hoje o alvo é `list(env.minerals)[5]`, puro
   acaso do sorteio: o A* não escolhe nada, só desenha a rota de quem já foi decidido.
4. **A base de regras.** É por isso que o caminho atual **pisa numa Prata e segue em frente**.
5. **Filtrar os minerais inalcançáveis da lista.** O `astar` detecta (`path is None`), mas ninguém
   filtra. De 600 casos, 25 vieram inalcançáveis — é o caso que o enunciado avisa: minérios cercados
   por paredes existem.

Os parâmetros já estão prontos em `domain.py` e sem uso: `INITIAL_BATTERY`, `STEP_BATTERY_COST`,
`TRAP_BATTERY_COST`, `MAX_CARGO_CAPACITY`, `DELIVERY_BONUS_PER_ITEM`, `BATTERY_SECURITY_THRESHOLD`.



