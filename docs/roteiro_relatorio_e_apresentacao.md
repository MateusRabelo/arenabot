# Roteiro do Relatório Técnico e da Apresentação

## 1. Estrutura do Relatório Técnico (PDF - 10 a 15 páginas)

### Capa e Identificação
- Título: Projeto Prático 01 - Sistema Competitivo de Coleta (Arena Bot)
- Identificação dos integrantes e divisão de tarefas
- Declaração explícita de uso de ferramentas de IA (conforme exigido na Seção 7.2)

### Passo 0 - Fundamentação Teórica
- Breve introdução conceitual sobre os quatro tópicos de IA Clássica:
  - Modelagem de Agentes Inteligentes
  - Busca Heurística no espaço de estados
  - Teoria dos Jogos e Busca Competitiva
  - Representação de Conhecimento e Raciocínio Lógico

### Passo 1 - Modelagem do Agente
- Tabela PEAS completa (Performance, Environment, Actuators, Sensors)
- Justificativa aprofundada das 6 propriedades do ambiente baseada estritamente no Arena Bot:
  1. Totalmente Observável
  2. Determinístico
  3. Sequencial
  4. Estático
  5. Discreto
  6. Multiagente Competitivo
- Descrição da arquitetura do agente (Agente Baseado em Utilidade) com diagrama de blocos
- Detalhamento dos atributos do estado interno do agente

### Passo 2 - Navegação com A*
- Formulação formal do problema de busca (Estados, Estado Inicial, Ações, Transição, Objetivo, Custo de Passo assimétrico)
- Prova matemática de que a heurística de Manhattan é admissível ($h(n) \le h^*(n)$)
- Prova matemática de que a heurística de Manhattan é consistente/monótona ($|h(n) - h(n')| \le c(n, n')$)
- Discussão comparativa entre Manhattan e Euclidiana (por que Manhattan domina e expande menos nós em vizinhança-4)
- Tratamento algorítmico para minérios inalcançáveis (detecção de nós sem caminho)

### Passo 3 - Busca Competitiva com Minimax e Poda Alfa-Beta
- Formulação do jogo estratégico (Estados, Ações, Transição, Função de Utilidade em folhas)
- Justificativa do Minimax operar em nível macro (escolha de minérios) em vez de células
- Definição formal da função de avaliação $Eval(m)$ com fator de ponderação de distância $\omega$
- Diagrama ilustrado de uma árvore Minimax com no mínimo 2 níveis, destacando:
  - Valores repassados nos nós MAX e MIN
  - Ramos explicitamente podados pelo critério $\alpha \ge \beta$
  - Justificativa passo a passo de cada corte

### Passo 4 - Validação por Base de Conhecimento
- Tabela de símbolos proposicionais e seus significados operacionais
- As 4 regras formais em Cláusulas Horn Definidas (as 2 obrigatórias e as 2 autorais)
- Descrição do algoritmo de inferência por Encadeamento para Frente (*Forward Chaining*)
- Tabela de rastreamento com 3 situações reais de partida:
  - Situação 1: Coleta autorizada com sucesso
  - Situação 2: Carga máxima atingida (forçando retorno)
  - Situação 3: Prevenção de pane seca por bateria crítica

### Seção de Resultados Experimentais
- Tabela do Torneio de 30 partidas (sementes 1 a 30):
  - Vitórias de Alfa, Vitórias de Beta, Empates
  - Pontuação média e desvio padrão
  - Duração média da partida em turnos
- Tabela e gráfico do benchmark de navegação:
  - Média de nós expandidos: A* versus BFS/UCS
  - Custo médio do caminho e tempo de execução
- Tabela e gráfico do efeito da poda alfa-beta:
  - Nós avaliados no Minimax com poda versus sem poda para $d \in \{2, 4, 6\}$
  - Percentual de nós economizados por profundidade

### Limitações e Trabalhos Futuros
- Análise crítica de pontos de melhoria (ex: coordenação cooperativa, aprendizado por reforço para ajuste dinâmico do $\omega$, suporte a armadilhas dinâmicas)

### Referências Bibliográficas
- Russell, S., & Norvig, P. Artificial Intelligence: A Modern Approach.
- Notas de aula da disciplina RUS0086 (Prof. Alan Rocha).

---

## 2. Roteiro de Apresentação (Slides - 10 a 15 minutos)

| Slide | Conteúdo | Tempo Estimado |
|---|---|---|
| 1 | Equipe, contextualização e visão geral do Arena Bot | 1,0 min |
| 2 | Formulação PEAS e as 6 propriedades do ambiente | 1,5 min |
| 3 | A*: Heurística de Manhattan, prova de admissibilidade e rotas | 2,0 min |
| 4 | Minimax estratégico: árvore de exemplo e poda $\alpha$-$\beta$ | 2,5 min |
| 5 | Base de Conhecimento: regras de Horn e caso de coleta bloqueada | 2,0 min |
| 6–7 | Resultados dos experimentos (Torneio, A* vs BFS, Nós com/sem poda) | 3,0 min |
| 8 | Demonstração ao vivo da partida no terminal | 2,0 min |
| 9 | Limitações, aprendizados e conclusão | 1,0 min |
