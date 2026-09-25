# Mapa de Arquivos e Arquitetura do Projeto

Este documento detalha a finalidade de cada diretório e arquivo do projeto **Arena Bot**, especificando suas responsabilidades, classes, funções principais e o tópico da ementa de Inteligência Artificial correspondente.

---

## 1. Visão Geral da Árvore de Diretórios

```text
arenabot/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── domain.py            # Estruturas fundamentais, coordenadas e enums
│   │   └── environment.py       # Grade 15x9, geração procedural com seed e regras físicas
│   ├── search/
│   │   ├── __init__.py
│   │   ├── astar.py             # Algoritmo A* com métricas de expansão e custo assimétrico
│   │   └── baseline_search.py   # Busca em Largura (BFS) para benchmark comparativo
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py    # Símbolos proposicionais e cláusulas de Horn
│   │   └── inference_engine.py  # Motor formal de encadeamento para frente (Forward Chaining)
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── evaluation.py        # Função heurística de avaliação Eval(m) calibrada
│   │   └── minimax.py           # Minimax recursivo com poda alfa-beta configurável
│   ├── agent/
│   │   ├── __init__.py
│   │   └── robot_agent.py       # Agente baseado em utilidade, telemetria e ciclo de 4 etapas
│   └── views/
│       ├── __init__.py
│       └── terminal_view.py     # Renderizador ASCII colorido e HUD informativo
├── experiments/
│   ├── __init__.py
│   ├── tournament.py            # Execução das 30 partidas do torneio (sementes 1 a 30)
│   ├── search_benchmark.py      # Comparação empírica de nós expandidos (A* vs BFS)
│   └── pruning_benchmark.py     # Medição de nós visitados pelo Minimax com vs sem poda
├── docs/
│   ├── guia_projeto_ia.md       # Guia teórico e formulação matemática completa
│   ├── roteiro_relatorio_e_apresentacao.md # Esqueleto do relatório técnico e slides
│   └── mapa_de_arquivos_e_arquitetura.md   # Este documento
├── main.py                      # Execução de partida individual interativa
├── run_experiments.py           # Execução da bateria completa de experimentos obrigatórios
├── pyproject.toml               # Configuração do projeto e dependências (uv)
└── .gitignore                   # Regras de exclusão do controle de versão
```

---

## 2. Detalhamento dos Módulos do Pacote `src/`

### 2.1 `src/core/` (Domínio e Física do Jogo)
Não contém inteligência artificial; modela as entidades e regras fundamentais da arena.

- **`domain.py`:**
  - `Position`: Tupla nomeada ou dataclass imutável `(x: int, y: int)` com cálculo de distância Manhattan e vizinhança ortogonal.
  - `MineralType`: Enum definindo os tipos e valores exatos de minérios da Tabela 1:
    - Diamante: 100 pontos
    - Rubi: 80 pontos
    - Ouro: 50 pontos
    - Prata: 30 pontos
    - Bronze: 10 pontos
  - `CellType`: Enum para tipos de células da grade (`LIVRE`, `PAREDE`, `ARMADILHA`).
- **`environment.py`:**
  - `ArenaEnvironment`: Classe que armazena a grade $15 \times 9$, conjuntos de coordenadas de 25 paredes, 6 armadilhas, dicionário de minérios disponíveis e coordenadas das bases em $(0,0)$ e $(14,8)$.
  - `generate_arena(seed: int)`: Geração determinística baseada na semente; assegura as células protegidas das bases e seus vizinhos ortogonais imediatos.
  - `get_valid_neighbors(pos: Position)`: Retorna vizinhos ortogonais válidos (dentro dos limites e excluindo paredes).

---

### 2.2 `src/search/` (Navegação com Busca Heurística - Unidade 3A)
Responsável por determinar trajetos ótimos e coletar métricas de desempenho de busca.

- **`astar.py`:**
  - `manhattan_distance(p1, p2)`: Heurística admissível e consistente $|x_1 - x_2| + |y_1 - y_2|$.
  - `find_path_astar(arena, start, goal)`: Implementação de A* com `heapq`, aplicando custo assimétrico (passo normal = 1; armadilha = 2).
  - Retorna `(caminho, custo_total, nós_expandidos)`. Caso o alvo esteja isolado por paredes, retorna `(None, inf, nós_expandidos)`.
- **`baseline_search.py`:**
  - `find_path_bfs(arena, start, goal)`: Implementação de Busca em Largura (BFS).
  - Serve como linha de base experimental para demonstrar a eficiência do A* na redução de nós expandidos.

---

### 2.3 `src/logic/` (Validação por Base de Conhecimento - Unidade 4)
Garante que decisões críticas (coleta e retorno) passem obrigatoriamente por inferência formal.

- **`knowledge_base.py`:**
  - Define símbolos atômicos: `B_ALTA`, `C_CHEIA`, `S_MINERIO`, `A_ADJ`, `B_CRITICA`, `P_COLETA`, `P_DESCARGA`, `R_CAUTELA`.
  - `HornClause`: Estrutura formal que encapsula regras no formato $Premissas \implies Conclusao$.
  - Catálogo com as 4 regras mínimas:
    1. $B_{alta} \land \neg C_{cheia} \land S_{minerio} \implies P_{coleta}$ (Obrigatória)
    2. $C_{cheia} \implies P_{descarga}$ (Obrigatória)
    3. $B_{critica} \implies P_{descarga}$ (Autoral: prevenção de pane seca)
    4. $A_{adj} \land B_{media} \implies R_{cautela}$ (Autoral: desvio de armadilha com bateria moderada)
- **`inference_engine.py`:**
  - `forward_chaining(facts: set[str], rules: list[HornClause])`: Algoritmo de encadeamento para frente até convergência (ponto fixo).
  - Gera log estruturado de regras disparadas para compor a tabela de rastreamento do relatório.

---

### 2.4 `src/strategy/` (Busca Competitiva - Unidade 3B)
Define qual minério perseguir ou se o robô deve recuar para a base através de teoria dos jogos.

- **`evaluation.py`:**
  - `evaluate_state(state, mineral)`: Calcula o valor heurístico de corte na profundidade $d$:
    $$Eval(m) = (pts_A - pts_B) + valor(m) + \omega \cdot [dist(Beta, m) - dist(Alfa, m)]$$
  - Pondera a recompensa imediata com a vantagem posicional relativa.
- **`minimax.py`:**
  - `minimax_alpha_beta(state, depth, alpha, beta, is_max, use_pruning)`: Implementação recursiva em nível macro de alvos minerais.
  - Alterna entre MAX (Alfa) e MIN (Beta); executa podas quando $\alpha \ge \beta$.
  - Rastreia contagem precisa de nós avaliados (com e sem poda) para $d \in \{2, 4, 6\}$.

---

### 2.5 `src/agent/` (Agente Inteligente Integrado - Unidades 1 e 2)
Implementa a arquitetura de agente baseado em utilidade.

- **`robot_agent.py`:**
  - `RobotAgent`: Mantém o estado interno completo exigido pelo edital:
    - Posição atual `pos`
    - Bateria residual `battery` (inicial 100)
    - Carga atual `inventory` (máx 3)
    - Pontuação acumulada `score`
    - Coordenada da base `base_pos`
    - Alvo selecionado `current_target`
    - Caminho planejado `current_path`
    - Alvos ignorados `ignored_targets` (para evitar loops infinitos)
  - `step(arena, opponent)`: Orquestra o ciclo de 4 fases: Decisão $\to$ Navegação $\to$ Atuação $\to$ Validação Lógica.

---

### 2.6 `src/views/` (Interface com o Usuário)

- **`terminal_view.py`:**
  - Renderiza o tabuleiro no terminal em ASCII com sequências de escape ANSI:
    - `[A]` (Azul ciano para Alfa)
    - `[B]` (Vermelho magenta para Beta)
    - `[#]` (Cinza para paredes)
    - `[!]` (Amarelo/Laranja para armadilhas)
    - `[♦]` (Cores variadas por raridade de minério)
  - Exibe HUD lateral com bateria, carga, pontuação e status das inferências da base de conhecimento.

---

## 3. Detalhamento dos Módulos do Pacote `experiments/`

Módulo dedicado a gerar os dados empíricos para o relatório técnico:

- **`tournament.py`:** Executa 30 partidas com sementes $s \in [1, 30]$ sem interface visual para medir taxa de vitórias de Alfa, vitórias de Beta, empates, médias, desvio padrão e turnos médios.
- **`search_benchmark.py`:** Compara 50 a 100 rotas entre A* e BFS, extraindo a média de nós expandidos e tempo de execução.
- **`pruning_benchmark.py`:** Executa Minimax com e sem poda nas profundidades $d = 2, 4, 6$, registrando nós visitados e porcentagem de redução.

---

## 4. Scripts Raiz

- **`main.py`:** Inicializa e executa uma partida individual visualizável no terminal, aceitando parâmetros de linha de comando (ex: `--seed 42`, `--delay 0.15`).
- **`run_experiments.py`:** Executa a suíte de experimentos de ponta a ponta e imprime as tabelas estatísticas prontas para inclusão no relatório técnico.
