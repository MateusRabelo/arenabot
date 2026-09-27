# ArenaBot — branch `astar`

Navegação do ArenaBot: geração do ambiente + **A\*** como algoritmo de pathfinding, com **BFS**
como algoritmo de referência para comparação.

Esta branch entrega **a rota, não o jogo**. Ela responde *"como eu chego nesse alvo"* e nada mais.
Não existe turno, não existe robô, não existe bateria sendo gasta, não existe escolha de alvo.
Se você está implementando a parte de cima (o ciclo do turno, a escolha de alvo, a base de
regras), esta branch é o seu piso — e a leitura principal deste README é a
[seção 4: o contrato do `search`](#4-o-contrato-do-search--leia-esta-se-vai-implementar-em-cima).

---

## 1. Como rodar

```bash
uv run python main.py
```

Saída: uma arena 15x9 desenhada **duas vezes lado a lado** (a original à esquerda, a mesma com o
caminho do A\* marcado em `*` à direita), o relatório de minerais e bateria, e embaixo a comparação
A\* contra BFS.

```
ORIGINAL          COM CAMINHO
#################   #################
#AA..#.#S.S.....#   #*A..#.#S.S.....#
#A.#.#....#....##   #*.#.#....#....##
#......!.....C..#   #******!.....C..#
#C..##..!#.#.#..#   #C..##*.!#.#.#..#
#C.#.!.........C#   #C.#.!*........C#
#.#.#.S........##   #.#.#.****.....##
##..C...#.R.!.G##   ##..C...#**.!.G##
#.#.....#.!.##.B#   #.#.....#.!.##.B#
##.R..!##..D..BB#   ##.R..!##..D..BB#
#################   #################
# Minerais: 12
# Bateria A: 100%
# Bateria B: 100%
alvo: Position(x=9, y=6) | passos: 15 | custo: 15 | expandidos: 34
A*: custo 15, 34 nos, 0.343 ms
BFS: custo 15, 74 nos, 0.606 ms
```

**Trocar o alvo** — `main.py:15`:

```python
goal = list(env.minerals)[5]     # o rubi
```

Índice de 0 a 11, na ordem de inserção do sorteio. Para ver a lista:

```python
env = Environment(seed=1)
for i, (p, t) in enumerate(env.minerals.items()):
    print(i, p, t.name)
```

**Trocar de arena** — mude o `seed` em `main.py:11`. Mesma seed, mesma arena, sempre.

**Detalhe de import:** `main.py:3` faz `sys.path.append("src")`. Sem isso o
`from core.domain import ...` não acha o pacote, porque o `uv` **não instala** o nosso código
(não há `[build-system]` no `pyproject.toml`, então o uv trata o projeto como virtual). Se você
criar um módulo novo em `src/`, mantenha essa linha ou converta o projeto em pacote de verdade.

---

## 2. Mapa de arquivos

| Arquivo | Linhas | O que faz |
|---|---|---|
| `src/core/domain.py` | 62 | Só dados e tipos. Parâmetros do jogo, `Position`, `MineralType`, onde ficam as bases. **Nenhuma lógica.** |
| `src/core/environment.py` | 134 | Gera a arena, sabe se imprimir, guarda a bateria de A e B. |
| `src/core/search.py` | 102 | A navegação: A\*, BFS e a comparação entre os dois. |
| `main.py` | 30 | Script de execução. Escolhe a arena, o alvo, chama a busca e imprime. |

---

## 3. O grafo que o `search` enxerga

O `search.py` **não recebe um grafo montado**. Ele recebe a `Environment` e faz duas perguntas ao
grid, uma por caractere:

- `"#"` → parede, não entra no grafo (`search.py:13`)
- `"!"` → armadilha, entra com custo dobrado (`search.py:22`)

Todo o resto é chão. Ou seja, **minerais são atravessáveis e não custam nada** — o caminho atual
pisa numa Prata e segue em frente, sem coletar nada, porque a base de regras da seção 4.4 ainda não
existe.

### Custo assimétrico

```python
def step_cost(env, nxt):
    if env.grid[nxt.y][nxt.x] == trap:
        return GRAPH_COST_TRAP   # 2
    return GRAPH_COST_NORMAL    # 1
```

Repara no argumento: o custo é lido do **destino** `nxt`, nunca da origem. Então
`c(n, n') ≠ c(n', n)`. É assimétrico de propósito, e é isso que faz o robô **contornar** a armadilha
em vez de atravessar: atravessar custa 2, dar a volta custa 1 por passo extra, então vale a volta
quando ela for curta.

**Por que 1/2 no grafo e não 2/4 da bateria?** A proporção é a mesma (dobrada), então o caminho ótimo
é idêntico. A bateria é uma conta separada, que ainda vai precisar de `STEP_BATTERY_COST` e
`TRAP_BATTERY_COST`.

### O que o A\* **não** sabe

O `search.py` inteiro não tem nenhuma menção a mineral. Ele só sabe que existe um custo diferente
para a armadilha, **não** que existe "bateria". Quem escolhe o mineral é a etapa anterior do turno
(o Minimax da seção 4.3, que não é escopo desta branch). O A\* funciona igual para mineral, para
base, para qualquer célula.

---

## 4. O contrato do `search` — leia esta se vai implementar em cima

Tudo em `src/core/search.py`. Todas as funções recebem a `Environment` como primeiro argumento;
não há estado global.

### `astar(env, start, goal)`

`search.py:36`

```python
path, cost, expanded = astar(env, start, goal)
```

| Retorna | Quando |
|---|---|
| `(caminho, custo, nós_abertos)` | existe rota |
| `(None, inf, n)` | alvo inalcançável |

O caminho é uma **lista de `Position`**, começando em `start` e terminando em `goal`. Portanto:

- `len(path) - 1` é o número de passos
- para o robô andar um passo, use `path[1]` — **não** a lista inteira
- `expanded` é o contador de nós abertos, que o enunciado pede na seção 6

`inf` é o `float("inf")` de `search.py:7`, não um número grande. Se você for serializar o resultado,
trate o `None` antes de olhar o custo.

### `bfs(env, start, goal)`

`search.py:73`. Mesma assinatura e mesmos retornos. Está aqui porque a seção 4.2 item 4 exige
comparar com um algoritmo de referência, e o BFS dá o contraste didático mais forte possível: ele
minimiza **número de passos**, não custo. Como aqui o custo é assimétrico, o BFS **não acha o
caminho mais barato** — acha o caminho mais curto em células e pode dar de cara com uma armadilha.
É exatamente a desvantagem que o item 4 quer discute.

### `compare(env, start, goal)`

`search.py:95`. Roda os dois na mesma arena e mede custo, nós abertos e tempo com
`time.perf_counter()`.

```python
results = compare(env, start, goal)
results["A*"]["path"]      # lista de Position
results["A*"]["cost"]      # int ou inf
results["A*"]["expanded"]  # int
results["A*"]["time"]      # float, em segundos
```

### Auxiliares

| Função | O que faz |
|---|---|
| `is_walkable(env, pos)` | `search.py:10`. Bounds + parede. **Use sempre antes de indexar o grid.** |
| `walkable_neighbors(env, pos)` | `search.py:16`. Vizinhança-4 já filtrada por `is_walkable`. |
| `step_cost(env, nxt)` | `search.py:21`. Custo de entrar em `nxt`. |
| `rebuild_path(came_from, goal)` | `search.py:27`. Remonta a rota a partir do dicionário `came_from`. |

### `Position` — `domain.py:35`

```python
@dataclass(frozen = True)
class Position:
    x: int
    y: int

    def manhattan_distance(self, other_pos) -> int: ...
    def neighbors(self) -> list["Position"]: ...   # 4-vizinhos, sem bounds check
```

`frozen=True` significa que ela é **hashable** — é por isso que dá para usar `Position` como chave de
dicionário e como elemento de `set` no A\*. Não muta, não precisa.

`neighbors()` pode devolver `x = -1` ou `y = -1` na borda. A moldura de `#` da tela **não existe no
grid** — é só impressão, em `show` e `show_with_path`. O grid tem 15x9 de verdade, então é
`is_walkable` que segura a borda.

### `Environment` — `environment.py:49`

```python
env = Environment(seed=1)          # ou seed=None para sorteio novo
env.width, env.height              # 15, 9
env.grid[y][x]                     # lista de listas de str de 1 caractere
env.minerals                       # dict {Position: MineralType}
env.battery_a, env.battery_b       # int, 100 no início
env.show()                         # imprime uma arena
env.show_with_path(path)           # imprime duas arenas, a da direita com o caminho
```

`env.minerals` é um `dict` indexado por `Position` (não por tupla) e os valores são `MineralType`, que
é um `Enum` com o valor em pontos: `DIAMOND=100`, `RUBY=80`, `GOLD=50`, `SILVER=30`, `COPPER=10`.
`MineralType.get_points()` (`domain.py:60`) devolve esse número. **Ninguém chama** — é a porta de
entrada para a escolha de alvo.

---

## 5. Como o A\* funciona aqui

### Estruturas

| Nome | O que é |
|---|---|
| `frontier` | a fila de prioridade, `heapq`. Tupla `(f, counter, g, posição)` |
| `cost_so_far` | o `g` de cada célula: menor custo já encontrado até ela |
| `came_from` | de onde cada célula veio, para remontar o caminho |
| `closed` | células já abertas, que não precisam ser reexpandidas |
| `expanded` | contador de nós abertos |

### O laço

```
while a fila não estiver vazia:
    tira o nó de menor f                       (heappop)
    se é o alvo: devolve o caminho e o custo
    se já estava em closed: pula               (duplicado na fila)
    marca em closed e conta em expanded
    para cada vizinho andável:
        se o novo custo é menor que o g que ele já tinha:  (relaxamento)
            atualiza o g, guarda o veio-de, empurra com o f novo
```

A tupla do heap é `(f, counter, g, posição)`, então o `heapq` desempata sempre pelo menor `f`, e o
`counter` impede que a comparação chegue no `Position`. Ver [armadilha 1](#armadilha-1).

### A heurística: Manhattan

`h` está em `domain.py:39`, dentro da `Position`. A fórmula é `f(n) = g(n) + h(n)`, com o `g`
entrando em `search.py:66`:

```python
f_next = new_cost + nxt.manhattan_distance(goal)
```

Não existe uma função `h()` separada: reaproveitar o método do `domain.py` evita duplicar a conta
e mantém a nomenclatura em inglês exigida pela regra de originalidade.

**Admissível** — qualquer rota de `n` até o alvo tem pelo menos `manhattan(n, alvo)` passos, porque
cada passo move 1 célula em uma coordenada por vez; e cada passo custa no mínimo 1. Logo o custo
real é sempre ≥ Manhattan, logo `h(n) ≤ h*(n)`.

**Consistente** — `|h(n) − h(n')| ≤ 1` porque um passo muda a Manhattan em no máximo 1, e
`1 ≤ c(n, n')` porque nenhum passo custa menos que 1. Logo `|h(n) − h(n')| ≤ c(n, n')`. Consequência
prática: o `closed` é seguro, **nenhum nó precisa ser reaberto**.

Foi conferido numericamente em 50 arenas: 16.206 arestas testadas para consistência e 64.562 células
testadas para admissibilidade (contra um Dijkstra reverso escrito só para o teste). Zero violações
nos dois casos.

**Por que não a Euclidiana** — ela também é admissível, e por isso engana: em vizinhança-4 não existe
diagonal, então ela subestima de mais de 25%. Numa grade 15x9, ir de (0,0) a (14,8) dá Euclidiana
≈ 16,1, mas o menor caminho real são 22 passos. O A\* quase não ganha direção e acaba se parecendo
com busca em largura. A Manhattan é exatamente o custo real sem armadilha, então guia a busca
certinho. (Se o movimento fosse 8-vizinhos, a Euclidiana seria a correta.)

---

## 6. Como encaixar no ciclo de turno

A parte que falta é o **passo 3 do turno** (seção 3.2): avançar uma célula do caminho e pagar o
custo de bateria. Hoje, depois de rodar o `main.py` inteiro, `battery_a` e `battery_b` continuam
**100** — o A\* devolve a rota e ninguém anda.

O esqueleto de um turno, para quem for construir em cima:

```python
from core.domain import ALFA_BASE, GRAPH_COST_TRAP, STEP_BATTERY_COST, TRAP_BATTERY_COST
from core.environment import trap
from core.search import astar, walkable_neighbors

position = Position(*ALFA_BASE[0])
cargo = []                                        # [(MineralType, pontos), ...]

while bateria_acima_do_limite():
    candidatos = [m for m in env.minerals if m != position]

    # 1. decidir: qual mineral? (Minimax com poda alfa-beta, seção 4.3 — não é desta branch)
    alvo = escolher_alvo(candidatos, cargo, position)

    # 2. navegar
    path, custo, expandidos = astar(env, position, alvo)
    if path is None:
        remover_da_lista_de_candidatos(alvo)       # seção 4.1: mineral cercado por parede
        continue

    # 3. atuar: um passo por turno
    proxima = path[1]
    if len(cargo) < MAX_CARGO_CAPACITY and env.grid[proxima.y][proxima.x] in mineral_chars:
        coletar(proxima)                           # seção 4.4: base de regras, ainda não existe

    # 4. validar
    position = proxima
    env.battery_a -= TRAP_BATTERY_COST if env.grid[position.y][position.x] == trap \
                    else STEP_BATTERY_COST
```

Quatro decisões que valem deixar explícitas:

1. **A posição inicial é um mineral de sorteio, não uma escolha.** Hoje é `list(env.minerals)[5]`, o
   **índice 5 da ordem de inserção**, ou seja, puro acaso do sorteio. Parece que o A\* "escolheu o
   rubi" e não escolheu nada: ele só desenha a rota de quem já foi decidido. Na seed 1 o índice 0 é
   um diamante, na seed 2 uma prata, na seed 3 um rubi.
2. **Um passo por turno, não o caminho inteiro.** `path[1]`, sempre. O `path` é o plano, não a
   ação — a arena pode mudar entre o planejamento e a execução.
3. **Replanejar é barato.** Os nós expandidos ficam na casa das dezenas (média 26,5). Não vale a pena
   tentar ser esperto com cache de rota: chame `astar` de novo a cada turno.
4. **Remover inalcançáveis da lista.** O `astar` já devolve `None` corretamente, mas **ninguém está
   filtrando** a lista de minerais. Com 600 casos, 25 minerais vieram inalcançáveis, e um flood fill
   independente concordou em 100% deles — é exatamente o caso que a seção 4.1 avisa: *"minérios
   cercados por paredes existem"*.

---

## 7. Resultados medidos

Semente fixa, como a seção 6 exige. Foram 30 seeds (1 a 30), da base Alfa para **cada** mineral de
cada arena. 360 casos, 24 dos quais com mineral inalcançável, sobrando 336 alcançáveis.

| Métrica | A\* | BFS |
|---|---|---|
| custo médio | 11,67 | 11,95 |
| nós expandidos (média) | 26,5 | 52,7 |
| tempo médio | 0,329 ms | 0,491 ms |
| vezes mais barato | — | 1,02x mais caro |
| vezes mais nós | — | 1,99x mais nós |

Nos 336 casos alcançáveis:

| | casos |
|---|---|
| A\* mais barato que BFS | 86 |
| empate | 250 |
| **A\* mais caro que BFS** | **0** |
| **A\* abrindo mais nós que BFS** | **0** |

Os 86 casos em que o A\* ganha no custo são a evidência concreta do efeito da armadilha: é onde
contornar sai mais barato que atravessar, e o BFS, preso no número de passos, atravessa.

### O caso para mostrar no relatório

O melhor exemplo está na **própria seed 1**, no mineral de índice 2, um Ouro em (13,6):

| | passos | custo | nós | armadilhas no caminho |
|---|---|---|---|---|
| A\* | 19 | **19** | 45 | 0 |
| BFS | 19 | **20** | 103 | 1 |

O detalhe que fecha a discussão: os dois fazem **19 passos**. O BFS não está errado, ele minimiza
número de passos e 19 é o mínimo. Só que um desses passos cai numa armadilha, que vale 2 em vez de 1, e
o custo vai a 20. O A\* chega no mesmo número de passos com custo 19, porque desvia. Esse caso mostra
as duas coisas de uma vez: o A\* é mais barato **e** abre menos da metade dos nós.

Se for escolher um caso único, tem que ser esse ouro de (13,6), porque é o único que prova o motivo
de o A\* existir, e não só de ele ser mais rápido.

### Outras verificações que já passaram

- **custo do A\* = custo mínimo real**, contra um Dijkstra independente escrito só para teste, em 575
  casos alcançáveis de 50 seeds: zero divergências.
- **alvo inalcançável devolve `(None, inf, n)`** em vez de travar.
- **o caminho é contínuo, não atravessa parede, começa na origem e termina no alvo**, e o custo bate
  com a soma dos passos: 0 falhas em 600 casos.

---

## 8. Armadilhas

Todas essas custaram tempo. São fáceis de repetir.

<a id="armadilha-1"></a>
### O `heapq` comparando `Position` → `TypeError`

`heapq` compara a tupla inteira quando dois `f` empatam, e a última posição da tupla é um `Position`,
que é um `@dataclass(frozen=True)` **sem `__lt__`**. Com uma grade 15x9 de `f` inteiro, empate de `f`
é constante, então estoura na hora.

Solução: o contador de desempate de `search.py:37`, incrementado a cada `push` e colocado entre o `f`
e o `g` na tupla. A comparação nunca chega no `Position`.

### `Position` não compara com tupla

`Position(0,0) == (0,0)` dá `False` — dataclass só compara com a própria classe. Então
`if pos in protected` com `protected` sendo lista de tuplas daria `False` **sempre**, e a proteção
das bases não valeria, **sem dar erro nenhum**. Parece funcionar e está errado.

Solução: converter para `Position` antes, uma vez só (`environment.py:68`). Mais barato ainda:
comparar com a tupla mesmo, `if (pos.x, pos.y) in ...`.

### A moldura de `#` não está no grid

O grid tem 15x9 de verdade. A moldura é só impressão. `Position(0,0).neighbors()` devolve
`x = -1` e `y = -1`. O `is_walkable` já trata isso, mas na hora de fazer o robô andar, lembre que a
borda da tela não é parede.

### Nome de constante colidindo com variável local

`path_char` em `environment.py:8` existe por causa disso: com `path = "*"`, o
`path, cost, expanded = astar(...)` do `main.py` criava uma local que escondia a constante, e
`env.grid[...] = path` gravava a **lista** no grid, quebrando o `show()` com
`TypeError: sequence item 0: expected str instance, list found`. Não repita o padrão com
`start`, `goal`, `cost`.

### Cores no terminal

`environment.py:44` — `if not sys.stdout.isatty(): colors = {}; reset = ""` é o que faz
`uv run python main.py > saida.txt` sair limpo. E `_colorize` só emite código onde tem cor no
dicionário, senão o relatório redirecionado vem inchado de `\033[0m` repetido. Confirme com
`uv run python main.py | cat -v` e veja que não aparece nenhum `^[`.

---

## 9. O que ainda não existe

Fronteira desta branch, para você não procurar código que não está aí:

- **O ciclo de turno (seção 3.2).** Nada executa turno.
- **O robô.** Não existe agente, carga, pontuação, nem quem escolhe a vez.
- **A escolha de alvo (seção 4.3, Minimax com poda alfa-beta).** Não é escopo desta branch.
- **A base de regras (seção 4.4, encadeamento para frente).** Não existe. É por isso que o caminho
  atual **pisa numa Prata e segue em frente**.
- **Remover os inalcançáveis da lista de candidatos (seção 4.1).** O `astar` detecta, a filtragem não.
- **O torneio de 30 partidas (seção 6 item 1).** Não existe, porque não existe jogo ainda.
- **`show()` está sem uso** (`environment.py:110`). Só o `show_with_path` é chamado pelo `main.py`.
  Deixei porque é o que vai servir para mostrar a arena limpa quando o turno entrar, mas se sobrar,
  pode ir.

### Parâmetros definidos e ainda não usados

Vários estão em `domain.py` prontos e **ninguém chama** — são para as partes que ainda não vieram:

| Parâmetro | Valor | Onde |
|---|---|---|
| Bateria inicial | 100 | `INITIAL_BATTERY`, linha 13 |
| Custo de passo normal | −2 de bateria | `STEP_BATTERY_COST`, linha 14 |
| Custo de passo em armadilha | −4 de bateria | `TRAP_BATTERY_COST`, linha 15 |
| Capacidade de carga | 3 minérios | `MAX_CARGO_CAPACITY`, linha 20 |
| Bônus por entrega | +10 | `DELIVERY_BONUS_PER_ITEM`, linha 21 |
| Limite de bateria segura | 10 | `BATTERY_SECURITY_THRESHOLD`, linha 22 |
| Pontos do mineral | 100/80/50/30/10 | `MineralType`, linha 53 — o grid usa o símbolo, `get_points()` **não** |

---

## 10. Regra de originalidade — atenção a isso

Trecho do enunciado, seção 2:

> Não é permitido: reutilizar os assets gráficos do jogo de referência; [...] copiar, renomear ou
> traduzir arquivos do projeto de referência ou de outra equipe; **entregar código gerado
> integralmente por ferramentas de IA sem compreensão**. O uso dessas ferramentas como apoio deve
> ser declarado no relatório, indicando o que foi gerado e como foi revisado.

Três coisas que foram cuidadas:

1. **O código do jogo de referência nunca foi aberto.** Só o PDF do enunciado, que é a especificação
   autorizada. Toda a implementação saiu do enunciado.
2. **A organização é diferente da referência.** A referência é um arquivo só com funções
   (`buscar_caminho`, `h`, `avaliar`); esta é um pacote `core/` com `domain`, `environment` e
   `search`, e nomes em inglês.
3. **A declaração de uso de IA precisa ir no relatório**: o que foi gerado (a estrutura do código,
   os comentários, a documentação) e como foi revisado (600 casos de teste, custo do A\* conferido
   contra um Dijkstra independente, admissibilidade e consistência verificadas em 50 arenas com zero
   violação).
