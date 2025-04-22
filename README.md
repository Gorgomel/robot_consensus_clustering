Claro! Aqui está o conteúdo completo do `README.md` diretamente no chat para você copiar e colar:

---

```markdown
# Projeto: Clusterização por Consenso Médio em Robôs Autônomos

Este projeto implementa e avalia heurísticas de clusterização aplicadas à coordenação de robôs autônomos conectados por um grafo de visibilidade espacial. O foco está em resolver um problema **NP-difícil de clusterização com restrições**, utilizando algoritmos como o **Método Guloso**, **Busca Local** e **Metaheurísticas**, comparando com resultados de datasets reais como o Reddit e RoadNet-CA.

---

## 📁 Estrutura do Projeto

```
PA/
├── data/
│   ├── cluster/               # Resultados das heurísticas e clusterizações
│   ├── grafo/                 # Grafo gerado (GraphML, CSV, imagens)
│   ├── plots/                 # Imagens geradas na análise
│   └── sinteticos/            # Dados sintéticos de robôs
│
├── ref/                       # Artigos de referência usados no projeto
│
├── src/                       # Código-fonte do projeto
│   ├── cluster_baselines/     # KMeans, Louvain, Agglomerativo, Spectral
│   ├── consensus/             # Grafo de coocorrência e consenso médio
│   ├── generate/              # Geração dos dados e visualizações
│   ├── graph/                 # Construção do grafo de visibilidade
│   └── heuristics/            # Guloso, Local Search, Metaheurística
│
├── tools/                     # Scripts utilitários e análise de datasets externos
│
├── config.py                  # Configurações globais do projeto
├── dataset.py                 # Carregamento e abstração dos datasets
├── metadados.txt              # Histórico de execuções, métricas e instâncias
├── README.md                  # Este arquivo
├── .gitignore                 # Arquivos/pastas ignorados pelo Git
```

---

## 📌 Objetivo Geral

Resolver um problema de **clusterização com restrições** que busca:

- Maximizar a **velocidade segura média** dentro de cada cluster
- Respeitar limites de comunicação (grafo ε-ball)
- Comparar heurísticas escaláveis com instâncias reais e sintéticas

---

## 🔁 Pipeline do Projeto

1. **Geração de Dados Sintéticos**  
   `src/generate/gerar_dados.py`  
   → Cria até 10.000 robôs simulando zonas densas e periféricas usando **Perlin Noise**

2. **Construção do Grafo de Conectividade**  
   `src/graph/construir_grafo.py`  
   → Conecta robôs com base em ε-ball, gera estatísticas e visualizações

3. **Clusterizações Base**  
   `src/cluster_baselines/`  
   → Aplica KMeans, Louvain, Spectral e Agglomerativo para comparação

4. **Grafo de Coocorrência**  
   `src/consensus/construir_coocorrencia.py`  
   → Cria um grafo ponderado com base nas coocorrências de agrupamento

5. **Algoritmos Heurísticos**  
   `src/heuristics/`  
   - `guloso_fo1.py` → algoritmo guloso baseado na FO1 (velocidade mínima ponderada)
   - `local_search.py` → refina solução gulosa
   - `metaheuristica.py` → PSO ou Simulated Annealing (em progresso)

6. **Visualização e Avaliação**  
   - NMI/ARI entre heurísticas e ground-truth (Reddit, sinteticos)
   - Gráficos de densidade, grau, velocidades, etc.

7. **Benchmarking com Datasets Reais**  
   - `Reddit` e `RoadNet-CA` adaptados com posição, velocidade e grau
   - Instâncias com até 5.000 nós

---

## ⚙️ Execução Básica

```bash
# 1. Gerar dados
python src/generate/gerar_dados.py

# 2. Construir grafo
python src/graph/construir_grafo.py

# 3. Executar heurística gulosa
python src/heuristics/guloso_fo1.py

# 4. Gerar clusterizações base
python src/cluster_baselines/kmeans.py
```

---

## 🔍 Função Objetivo FO1

```math
\text{FO}_1(C) = \sum_{k=1}^{K} \left( \min_{i \in C_k} v_i \right) \cdot |C_k|
```

- Maximiza a velocidade mínima ponderada por cluster
- A ser comparada com FO2 (penalização por violação) e FO3 (média harmônica robusta)

---

## 🧠 Status das Heurísticas

| Método               | Implementado | Avaliado | Integrado |
|----------------------|--------------|----------|-----------|
| Guloso (FO1)         | ✅ Sim        | ✅ Sim    | ✅ Sim     |
| Local Search         | 🔧 Em andamento | ❌       | ❌         |
| Metaheurística       | 🔧 Em planejamento | ❌       | ❌         |
| Clusterizações base  | ✅ Sim        | ✅ Sim    | ✅ Sim     |

---

## 📦 Datasets Externos

| Dataset       | Formato | Utilização     | Status  |
|---------------|---------|----------------|---------|
| Reddit        | GraphML | Comparação com subreddits (NMI/ARI) | ✅ |
| RoadNet-CA    | edge list | Simula mapa real (posições reais) | 🔧 |
| Cisco UCI     | CSV      | Velocidade via throughput | 🔧 |

---

## 📝 Requisitos

- Python 3.10+
- numpy, networkx, matplotlib, seaborn, scikit-learn
- (opcional) tqdm, community, scipy

---

## 🧹 Sugestões para `.gitignore`

```gitignore
venv/
__pycache__/
*.npy
*.npz
*.csv
*.png
*.graphml
data/**
!data/cluster/
!data/grafo/
!data/sinteticos/
*.txt
sizes.txt
```

---

## 🚀 Como Subir no GitHub

> Dica: Use `git lfs` para arquivos maiores que 50 MB (não subir `.npy`, `.npz` direto)

```bash
git init
git remote add origin https://github.com/SeuUsuario/NomeDoProjeto.git
git add .
git commit -m "v1: pipeline completo com heurística gulosa"
git push -u origin main
```

---

## 📚 Referências

- [Greedy Agglomerative Heuristic for Graph Clustering (2020)](https://example.com)
- [Consensus Clustering by Graph-based Approach (2018)](https://example.com)
- [Reddit Dataset on PapersWithCode](https://paperswithcode.com/sota/node-classification-on-reddit)

---

> Projeto acadêmico em andamento. Contribuições são bem-vindas!
```



# Clone o repositório
git clone https://github.com/Gorgomel/robot_consensus_clustering.git
cd robot_consensus_clustering

# Crie e ative o ambiente virtual (Windows)
python -m venv venv
.\venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt



O noise é usado para simular densidade espacial com Perlin Noise.

scikit-learn fornece KMeans, Agglomerative, Spectral Clustering, etc.

networkx cuida de leitura, escrita, visualização e análise de grafos.

scipy.spatial.cKDTree é usado para construir o grafo ε‑ball com eficiência.

tqdm aparece em várias etapas como barra de progresso.

seaborn é opcional, mas recomendado para melhorar os gráficos (ex: heatmaps).




---

## ⚙️ Ambiente de Desenvolvimento: Windows + WSL

Este projeto foi configurado para funcionar de forma eficiente no **Windows** com auxílio do **WSL (Windows Subsystem for Linux)**. Isso garante performance otimizada, uso de ferramentas Linux e compatibilidade com comandos de automação via `Makefile`.

### 📌 Por que usar WSL?

Alguns pacotes do projeto, como `noise`, possuem dependências que exigem compilação com ferramentas de desenvolvimento Linux (como `gcc` e `Python.h`). No Windows puro, isso pode gerar erros difíceis de resolver. O WSL contorna esses problemas com um ambiente Linux real dentro do Windows.

---

## 🧰 Requisitos para utilizar o WSL

1. **Instalar o Ubuntu via WSL**  
   Você pode usar o [Ubuntu 22.04.5 LTS](https://apps.microsoft.com/detail/ubuntu-22045-lts/9PN20MSR04DW) pela Microsoft Store.

2. **Acessar a pasta do projeto via WSL**  
   - Exemplo:
     ```bash
     cd /mnt/c/Users/Brunn/Desktop/PA-Novo
     ```

3. **Instalar ferramentas necessárias no Ubuntu**  
   Rode os seguintes comandos no terminal WSL:

   ```bash
   sudo apt update
   sudo apt install make python3-venv python3-dev build-essential
   ```

---

## 🐍 Criando o ambiente virtual no WSL

Este projeto utiliza um ambiente isolado dentro do WSL. Use o `Makefile` para criá-lo:

```bash
make create-venv-wsl
```

Se for a primeira vez, ele irá:
- Criar o ambiente em `~/.venvs/PA-Novo`
- Instalar as dependências do `requirements.txt`

---

## 💥 Problemas comuns e soluções

### ❌ Erro com `noise` e `Python.h`

Se durante a criação da venv você encontrar:

```
fatal error: Python.h: No such file or directory
```

Execute:

```bash
sudo apt install python3-dev
```

---

## 🚀 Usando o projeto no WSL

Uma vez configurado:

1. **Ative o ambiente**:

   ```bash
   source ~/.venvs/PA-Novo/bin/activate
   ```

2. **Gere os dados com**:

   ```bash
   make all
   ```

3. **Ou execute etapas específicas**:
   - `make data`
   - `make graph`
   - `make cluster`
   - `make evaluate`

---

## 🤖 Alternativa (avançado): Sincronização entre Windows e WSL

Para usuários avançados, há scripts para sincronizar o conteúdo entre um clone Windows e um clone Linux do projeto. Essa abordagem permite usar o VSCode no Windows e rodar os scripts no WSL. Os scripts estão em:

- `sync_to_wsl.sh`
- `sync_to_windows.sh`

---


### 🔁 Ambientes Virtuais no WSL

Este projeto utiliza ambientes virtuais fora da pasta do projeto, para evitar poluição e facilitar a organização. O ambiente virtual será criado no caminho:

```
~/.venvs/PA-Novo
```

#### 📌 Por que usar esse caminho?

- Impede que a pasta `venv/` apareça no GitHub ou polua o repositório.
- Permite centralizar todos os ambientes em um só lugar (`~/.venvs`).
- Facilita a troca entre projetos no WSL.

#### ⚙️ Como ativar o ambiente?

No terminal WSL:

```bash
source ~/.venvs/PA-Novo/bin/activate
```

Você verá o nome `(PA-Novo)` no início da linha do terminal, indicando que o ambiente está ativo.

#### 🧼 Como apagar/recriar?

Basta excluir a pasta:

```bash
rm -rf ~/.venvs/PA-Novo
```

Depois, crie novamente com:

```bash
make create-venv-wsl
```
