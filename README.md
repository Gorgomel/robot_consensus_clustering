# Projeto PA: Clusterização por Consenso Médio em Robôs

Este repositório contém:

- **Scripts de geração de dados sintéticos** (`src/generate/`)
- **Construção do grafo ε‑ball** (`src/graph/`)
- **Heurísticas**  
  - Algoritmo guloso (FO₁) (`src/heuristics/guloso_fo1.py`)  
  - Busca Local (`src/heuristics/local_search.py`)  
  - Metaheurística (`src/heuristics/metaheuristica.py`)  
- **Baselines** (KMeans, Agglomerativo, Louvain, Spectral) em `src/cluster_baselines/`
- **Ferramentas auxiliares** em `tools/`
- **Configuração** em `config.py`
- **Metadados** em `metadados.txt`  

### Como usar

1. Ajuste parâmetros em `config.py`.  
2. Gere os dados:
3. Construa o grafo:
4. Rode cada heurística (por exemplo):
5. Compare resultados, etc.

