# Guia Completo e Documentação Técnica: Arena Bot (PP01)
**Disciplina:** RUS0086 - Inteligência Artificial (UFC Russas - Semestre 2026.2)  
**Professor:** Alan Rocha  
**Projeto:** PP01 - Sistema Competitivo de Coleta

---

## 1. Visão Geral do Sistema e Arquitetura

O **Arena Bot** é um ambiente multiagente competitivo e determinístico em grade 2D ($15 \times 9$), onde dois agentes autônomos (**Alfa** e **Beta**) disputam minérios de valores distintos (10 a 100 pontos), gerenciando restrições de bateria, capacidade de armazenamento e obstáculos.

A tomada de decisão de cada agente opera em um ciclo fechado de quatro estágios a cada turno:

```text
       ┌────────────────────────┐
       │   1. DECISÃO MACRO     │  Minimax com Poda Alfa-Beta (d >= 4)
       │      "Aonde ir?"       │  Escolha estratégica do alvo ou retorno à base
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │   2. NAVEGAÇÃO MICRO   │  Busca Heurística A* (Manhattan)
       │     "Como chegar?"     │  Traçado de rota com desvio de armadilhas/paredes
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │      3. ATUAÇÃO        │  Física do Mundo / Execução de Passo
       │   "Avançar e Pagar"    │  Consumo de bateria (-2 normal / -4 armadilha)
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ 4. VALIDAÇÃO LÓGICA    │  Motor de Inferência por Encadeamento para Frente
       │    "Posso coletar?"    │  Cláusulas Horn definidas / Base de Conhecimento
       └────────────────────────┘
```

---

## 2. Modelagem do Agente e Ambiente (Unidades 1 e 2)

### 2.1 Formulação PEAS
- **Performance (Medida de Desempenho):** Pontuação total acumulada obtida pela coleta de minérios somada aos bônus de descarregamento na base (+10 por item), deduzida de eventuais penalidades ou empates.
- **Environment (Ambiente):** Grade bidimensional $15 \times 9$ (135 células), contendo 25 paredes intransponíveis, 6 armadilhas de bateria, 12 minérios de valores variados e duas bases nas extremidades opostas: Alfa em $(0,0)$ e Beta em $(14,8)$.
- **Actuators (Atuadores):** Movimentação discreta em vizinhança-4 (Norte, Sul, Leste, Oeste), atuador de coleta de minério na célula atual e atuador de descarga/recarga na célula da base.
- **Sensors (Sensores):** Sensor de localização espacial $(x, y)$, medidor de nível de bateria (0 a 100), contador de carga/inventário (0 a 3), detector de conteúdo da célula atual e radar de proximidade do adversário e armadilhas adjacentes.

### 2.2 Propriedades do Ambiente
1. **Totalmente Observável:** Em qualquer turno, o estado completo da grade (posições, obstáculos, minérios disponíveis e telemetria de ambos os robôs) é acessível sem oclusão ou névoa.
2. **Determinístico:** As ações de movimentação, coleta e recarga têm efeitos 100% previsíveis; não há falha mecânica aleatória ou estocasticidade nas transições de estado.
3. **Sequencial:** A decisão em um turno condiciona o nível de bateria remanescente, o inventário ocupado e os minérios ainda disponíveis nos turnos futuros.
4. **Estático:** O ambiente permanece imóvel e inalterado durante o processamento do algoritmo deliberativo do agente.
5. **Discreto:** Espaço de estados finito (135 células), conjunto de ações enumerável (4 movimentos + coletar/descarregar) e tempo medido em turnos discretos.
6. **Multiagente Competitivo:** Dois robôs disputam os mesmos recursos com objetivos opostos em relação ao placar final (jogo estratégico de soma zero).

### 2.3 Arquitetura do Agente
O robô é classificado como um **Agente Baseado em Utilidade**. Ele mantém estado interno (mapa, rota, inventário e histórico) e avalia múltiplos estados futuros através de uma função de utilidade contínua que pondera ganho de pontuação, custos de navegação e vantagem posicional sobre o adversário.

---

## 3. Navegação com A* e Algoritmo de Referência (Unidade 3A)

### 3.1 Formulação do Problema de Busca
- **Espaço de Estados:** Coordenadas inteiras $(x, y) \in [0, 14] \times [0, 8]$ correspondentes a células livres (excluindo coordenadas pertencentes ao conjunto de paredes).
- **Estado Inicial:** Posição atual do robô $(x_{agente}, y_{agente})$.
- **Ações:** $\Delta \in \{(0, 1), (0, -1), (1, 0), (-1, 0)\}$ respeitando limites e obstáculos.
- **Modelo de Transição:** $Resultado((x, y), (\Delta x, \Delta y)) = (x + \Delta x, y + \Delta y)$.
- **Teste de Objetivo:** $(x, y) = (x_{alvo}, y_{alvo})$.
- **Custo de Passo:**
  $$c(n, n') = \begin{cases} 2, & \text{se } n' \text{ é armadilha} \\ 1, & \text{caso contrário} \end{cases}$$

### 3.2 Heurística e Prova de Admissibilidade / Consistência
A heurística adotada é a **Distância de Manhattan**:
$$h(n) = |x_n - x_{alvo}| + |y_n - y_{alvo}|$$

- **Prova de Admissibilidade ($h(n) \le h^*(n)$):** O menor trajeto possível em grade com vizinhança-4 sem nenhum obstáculo possui comprimento exato de $|x_n - x_{alvo}| + |y_n - y_{alvo}|$. Como o menor custo possível por passo no grafo é $c_{min} = 1$, o custo real $h^*(n)$ jamais será inferior a $h(n) \times 1$. Logo, $h(n) \le h^*(n)$ é estritamente satisfeita.
- **Prova de Consistência ($h(n) \le c(n, n') + h(n')$):** Para quaisquer nós vizinhos $n$ e $n'$, a variação na distância de Manhattan é no máximo 1, isto é, $|h(n) - h(n')| \le 1$. Como o custo real de transição satisfaz $c(n, n') \ge 1$, tem-se $h(n) - h(n') \le c(n, n') \implies h(n) \le c(n, n') + h(n')$. A heurística é, portanto, monótona.
- **Comparação com Distância Euclidiana:** A distância Euclidiana $h_{euc}(n) = \sqrt{(x_n - x_{alvo})^2 + (y_n - y_{alvo})^2}$ também é admissível, porém $h_{euc}(n) \le h(n)$ para qualquer par de pontos em grade com movimentação ortogonal. Portanto, a distância de Manhattan é **estritamente mais informada** (domina a Euclidiana), garantindo menor expansão de nós na fronteira de busca.

### 3.3 Algoritmo de Referência para Benchmark
Para cumprimento do requisito experimental, implementa-se paralelamente a **Busca em Largura (BFS)** ou **Busca de Custo Uniforme (UCS)**, registrando:
- Total de nós expandidos por chamada.
- Custo do caminho encontrado.
- Tempo de execução em milissegundos.

---

## 4. Tomada de Decisão com Minimax e Poda Alfa-Beta (Unidade 3B)

### 4.1 Otimização Estratégica (Nível Macro)
O algoritmo Minimax opera sobre a escolha de **alvos (minérios)** e não sobre movimentos atômicos de grade, evitando a explosão combinatória do espaço de busca.

- **Estado Estratégico:** $s = \langle p_A, p_B, M, pts_A, pts_B, carga, bateria, vez \rangle$, onde $M$ é o conjunto de minérios disponíveis.
- **Espaço de Ações:** Escolher um minério $m \in M$ ou a ação `retornar_base`.
- **Transição:** O agente que seleciona $m$ simula o consumo de turnos correspondente ao caminho ótimo até $m$, pontua o valor associado, remove $m$ de $M$ e transfere a vez ao rival. Caso ambos selecionem o mesmo mineral no mesmo horizonte, o agente mais próximo assume a posse.
- **Profundidade:** $d \ge 4$ plies (duas rodadas completas de decisões estratégicas de ambos os robôs).

### 4.2 Função Heurística de Avaliação $Eval(m)$
Para nós cortados na profundidade limite $d$:
$$Eval(m) = (pts_A - pts_B) + valor(m) + \omega \cdot [d(p_B, m) - d(p_A, m)]$$
- $valor(m) \in [10, 100]$: Diamante (100), Rubi (80), Ouro (50), Prata (30), Bronze (10).
- $[d(p_B, m) - d(p_A, m)] \in [-22, 22]$: Vantagem espacial de proximidade.
- $\omega$: Coeficiente de balanceamento que equaliza a escala de pontos com a escala de distância, impedindo que a distância seja ignorada frente ao valor nominal do minério.

### 4.3 Poda Alfa-Beta
Durante a travessia em profundidade, mantêm-se os parâmetros:
- $\alpha$: Maior pontuação garantida pelo jogador MAX até o momento.
- $\beta$: Menor pontuação garantida pelo jogador MIN até o momento.
- **Condição de Corte:** Sempre que $\alpha \ge \beta$, o sub-ramo restante é podado sem alteração no resultado ótimo. Instrumenta-se a contagem explícita de nós avaliados com e sem poda.

---

## 5. Validação Lógica por Base de Conhecimento (Unidade 4)

### 5.1 Motor de Inferência por Encadeamento para Frente (*Forward Chaining*)
Nenhuma ação de coleta pode ser realizada por operadores condicionais simples (`if`). A autorização requer dedução formal por um motor baseado em Cláusulas de Horn Definidas:
$$\bigwedge_{i=1}^k Premissa_i \implies Conclusao$$

O motor opera iterativamente sobre o conjunto de fatos observados no turno atual até atingir o ponto fixo:
$$\text{Fatos}_{t+1} = \text{Fatos}_t \cup \{ Conclusao \mid \text{Premissas}(Regra) \subseteq \text{Fatos}_t \}$$

### 5.2 Base de Regras Formal
1. **Regra 1 (Obrigatória - Coleta Permitida):**
   $$B_{alta} \land \neg C_{cheia} \land S_{minerio} \implies P_{coleta}$$
2. **Regra 2 (Obrigatória - Descarga Obrigatória):**
   $$C_{cheia} \implies P_{descarga}$$
3. **Regra 3 (Autoral - Prevenção de Pane Seca):**
   $$B_{critica} \implies P_{descarga}$$
   *(Dispara quando a bateria residual é estritamente menor ou igual ao custo mínimo de retorno à base).*
4. **Regra 4 (Autoral - Alerta de Armadilha Adjacente):**
   $$A_{adj} \land B_{media} \implies R_{cautela}$$
   *(Altera o peso de penalidade de células vizinhas em caso de bateria moderada).*

---

## 6. Estrutura Autoral de Diretórios do Projeto

Para garantir total originalidade (Seção 2 do edital), adota-se a seguinte arquitetura modular:

```text
arenabot/
├── docs/
│   └── guia_projeto_ia.md       # Este documento
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── domain.py            # Enums, coordenadas, estruturas de dados
│   │   └── environment.py       # Grade 15x9, paredes, armadilhas, minérios
│   ├── search/
│   │   ├── __init__.py
│   │   ├── astar.py             # A* com fila de prioridade e rastreador de nós
│   │   └── baseline_search.py   # BFS/UCS para comparação de métricas
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── inference_engine.py  # Motor de forward chaining formal
│   │   └── knowledge_base.py    # Regras e símbolos proposicionais
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── minimax.py           # Minimax recursivo com poda alfa-beta
│   │   └── evaluation.py        # Função heurística Eval(m) ponderada
│   ├── agent/
│   │   ├── __init__.py
│   │   └── robot_agent.py       # Estado interno, telemetria e ciclo decisório
│   └── views/
│       ├── __init__.py
│       └── terminal_view.py     # Interface ASCII rica com cores ANSI e HUD
├── experiments/
│   ├── __init__.py
│   ├── tournament.py            # Execução das 30 sementes fixas
│   ├── search_benchmark.py      # Comparação A* vs BFS
│   └── pruning_benchmark.py     # Nós Minimax com vs sem poda (d=2, 4, 6)
├── main.py                      # Execução de partida individual
└── run_experiments.py           # Bateria completa de testes obrigatórios
```

---

## 7. Protocolo dos Experimentos Obrigatórios

1. **Torneio de 30 Partidas:**
   - Sementes fixas: $s \in \{1, 2, \dots, 30\}$.
   - Métricas: Vitórias de Alfa, Vitórias de Beta, Empates, Pontuação Média, Desvio Padrão e Média de Turnos.
2. **Custo de Busca (Navegação):**
   - Rastreamento da média de nós expandidos pelo A* versus BFS em 50 instâncias de rota.
3. **Efeito da Poda Alfa-Beta:**
   - Medição exata de nós avaliados com e sem poda nas profundidades $d = 2$, $d = 4$ e $d = 6$.
