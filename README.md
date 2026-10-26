# Arena Bot 00000010

Projeto prático de Inteligência Artificial integrando Busca Heurística (A*), Teoria dos Jogos (Minimax com Poda Alfa-Beta) e Lógica Proposicional (Encadeamento para Frente com Cláusulas de Horn).

---

## Como rodar

O projeto utiliza o gerenciador **uv** para gerenciar dependências e execução de forma rápida e isolada.

### 1. Instalar Dependências
```bash
uv sync
```

### 2. Comandos de Execução

- **Partida Normal (com mapa aleatório):**
  ```bash
  uv run python main.py
  ```

- **Torneio Oficial (executa as 30 sementes e gera a tabela estatística):**
  ```bash
  uv run python main.py --tournament
  ```

- **Benchmarks Obrigatórios (A* vs BFS e efeito da Poda Alfa-Beta):**
  ```bash
  uv run python main.py --benchmark
  ```

---