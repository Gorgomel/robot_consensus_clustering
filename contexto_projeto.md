# Projeto: Clusterização por Consenso Médio em Robôs Autônomos

Este projeto é parte de uma iniciativa de Iniciação Científica, TCC e futuro Mestrado, cujo objetivo geral é estudar e comparar **heurísticas e metaheurísticas aplicadas à coordenação de veículos autônomos heterogêneos em ambientes urbanos**, focando em problemas de **clusterização com restrições** que caracterizam **problemas NP-difíceis**.

---

## 🧠 Contexto Geral

Veículos autônomos em áreas urbanas precisam tomar decisões rápidas, locais e distribuídas, respeitando limites físicos, de visibilidade e comunicação. Neste projeto, modelamos essa situação como um problema de **clusterização dinâmica com restrições**, onde grupos de veículos devem ser formados respeitando:

- Distância máxima de comunicação (`ε`)
- Similaridade de atributos (principalmente **velocidade segura**)
- Conectividade no grafo local de visibilidade

A abordagem propõe aplicar:

- **Heurística Gulosa** (construção simples da solução)
- **Heurística de Refinamento** (como Busca Local)
- **Metaheurística** (como Simulated Annealing ou PSO)

E comparar os resultados com clusterizações obtidas por algoritmos clássicos (KMeans, Louvain etc.) em instâncias:

- **Sintéticas realistas** (com distribuição urbana)
- **Reais**, como os datasets **Reddit**, **RoadNet-CA** e **Cisco Secure Network**

---

## 🎯 Objetivo do Artigo Atual

O artigo atual é a primeira parte do projeto maior (IC/TCC/Mestrado), e tem como objetivo:

> Comparar o comportamento e desempenho de três estratégias heurísticas aplicadas à clusterização de veículos autônomos com restrições locais.

- A função objetivo (FO) foi definida de forma a **caracterizar o problema como NP-difícil**, e gerar resultados comparáveis.
- A FO escolhida para o Guloso é a **FO1**: `soma das menores velocidades seguras intra-cluster * tamanho do cluster`.

---

## 📐 Formulações de Função Objetivo (Resumo)

| FO     | Fórmula                                                                                 | Destaque                                |
|--------|------------------------------------------------------------------------------------------|------------------------------------------|
| **FO1** | `∑ min(v_i) * |C_k|`                                                                    | Usada no Guloso — rápida e segura        |
| **FO2** | `∑ max(v_i) - λ * penalidades`                                                         | Controla performance vs. violação        |
| **FO3** | `∑ média harmônica(v_i) - λ * penalidades`                                              | Suavidade, robustez — ideal p/ metaheur. |

---

## 🧪 Estratégia Heurística e Avaliação

As seguintes etapas compõem o pipeline do projeto:

## 1. Geração de Dados Sintéticos Escalonados e Realistas

Para garantir que os testes com heurísticas e metaheurísticas sejam significativos, foram projetadas instâncias sintéticas com alta complexidade estrutural, espacial e topológica. A seguir, são descritas as sete camadas de modelagem adotadas.

---

### 1.1 Escalonamento de Instâncias

Instâncias foram organizadas em três escalas:

| Nome     | Número de Robôs | Tamanho da Área (m²) | Aplicação Principal |
|----------|------------------|----------------------|---------------------|
| small    | 300              | 300×300              | Debug, validação    |
| medium   | 3.000            | 1.000×1.000          | Teste comparativo   |
| large    | 10.000           | 3.000×3.000          | Avaliação escalável |

Todas as instâncias compartilham parâmetros similares de densidade e estrutura, permitindo comparações controladas.

---

### 1.2 Topologia Espacial Híbrida

Foi adotada uma combinação entre **Perlin Noise (baixa frequência)** e **mixturas de gaussianas** para modelar a densidade urbana, criando:

- **Núcleos urbanos densos**
- **Zonas suburbanas de transição**
- **Áreas rurais esparsas**

Além disso, utilizou-se uma abordagem de **Grid Sampling + Jitter**, que garante distribuição uniforme com pequenas variações locais, evitando sobreposição excessiva.

---

### 1.3 Atributos Correlacionados com o Espaço

Os atributos dos robôs foram definidos com base na densidade da região:

- **Velocidade**: inversamente proporcional à densidade local:
  \[
    v_i \sim \mathcal{N}(\mu - \beta \cdot \rho(x_i), \sigma^2)
  \]
- **Bateria**: distribuída uniformemente, com leve correlação negativa com a densidade.
- **Outros atributos**: como direção, podem ser aleatórios se não participarem da FO.

---

### 1.4 Construção do Grafo de Visibilidade (ε-ball)

Utiliza-se uma **cKDTree** para identificar vizinhos em raio ε com complexidade \( O(n \log n) \). O grafo resultante:

- É esparso e localmente conexo
- Contém pesos (distância euclidiana entre robôs)
- Pode ser desconexo (teste de robustez)

---

### 1.5 Validação da Distribuição

Após cada geração de dados, são produzidas automaticamente:

- Heatmap de densidade espacial (Perlin + Gauss)
- Histogramas de velocidade e bateria
- Histograma de grau do grafo
- Curva radial de densidade (densidade por distância ao centro)
- Índice de Moran (autocorrelação espacial)

---

### 1.6 Integração com Instâncias Reais

Para comparação com dados reais, foram incorporados:

| Dataset       | Tipo     | Nós   | Adaptado para Robôs        |
|---------------|----------|-------|-----------------------------|
| roadNet-CA    | Viário   | 5.000 | Posições reais, grau → vel |
| Reddit (2k/5k)| Social   | 2k/5k | PCA dos embeddings, vel = log(grau+1) |

---

### 1.7 Pipeline Consolidado

O pipeline completo foi modularizado em:

1. `generate.py`: gera dados com escalas small/med/large
2. `build_graph.py`: constrói grafo ε-ball via KDTree
3. `cluster_*.py`: aplica heurísticas e salva resultados
4. `evaluate.py`: compara soluções (tempo, FO, NMI, ARI)

---

Com essas instâncias, o projeto é capaz de:

> Simular contextos urbanos de diferentes escalas e testar heurísticas sob restrições operacionais realistas, mantendo comparabilidade com grafos reais e reprodutibilidade para publicação científica.


### 2. Construção do Grafo

- Grafo não-direcionado baseado em conectividade `ε-ball`
- Nós conectados se `distância(x_i, x_j) < ε`
- Grafo salvo em `.graphml`, `.csv` e visualizações

### 3. Clusterização com Heurísticas

- Implementação de algoritmo **guloso FO1**
- Geração de rótulos e gráfico de clusters
- Salvo em `data/cluster/guloso_area_maior/`

### 4. Comparação com Clusterizações Clássicas

- Aplicados:
  - `KMeans` (vetorial)
  - `Louvain` (modularidade)
  - `Agglomerativo`
  - `Spectral`
- Resultados salvos em `data/cluster/` por método

### 5. Grafo de Coocorrência

- Criado a partir da frequência de coagrupamento entre pares de robôs nos diferentes métodos
- Serve como base para o consenso guloso

---

## 📊 Datasets Reais Utilizados

| Dataset          | Origem / Tipo                  | Adaptação p/ Robôs                         | Métrica de Avaliação     |
|------------------|-------------------------------|---------------------------------------------|---------------------------|
| **Reddit**       | Grafos sociais                | Embeddings como posição, grau como velocidade | NMI com subreddits        |
| **RoadNet-CA**   | Mapa rodoviário da Califórnia | Posição real, velocidade ∼ grau             | ARI com Spectral          |
| **Cisco Network**| Hosts de rede (UCI)           | Latência como distância, throughput como velocidade | NMI por latência          |

---

## 📂 Estrutura do Projeto

```
📦 PA/
├── config.py                # Parâmetros globais
├── metadados.txt            # Log técnico de versões e resultados
├── dataset.py               # Interface unificada para dados sintéticos e reais
├── data/
│   ├── sinteticos/          # robos.npy + visualizações da geração
│   ├── grafo/               # grafo_epsilon.graphml + estatísticas
│   ├── cluster/             # resultados das heurísticas
│   └── plots/               # gráficos auxiliares
├── ref/                     # Artigos científicos usados
├── src/
│   ├── generate/            # gerar_dados.py, plots.py
│   ├── graph/               # construir_grafo.py
│   ├── heuristics/          # guloso_fo1.py, local_search.py, metaheuristica.py
│   ├── consensus/           # construir_coocorrencia.py
│   ├── cluster_baselines/   # KMeans, Louvain, Agglomerativo, Spectral
│   └── processar_reddit_5k.py, visualizar.py
├── tools/                   # Scripts utilitários
└── README.md
```

---

## 🧠 Formulação Matemática

- **Grafo**: $G = (V, E)$, com $(i,j) \in E \iff d(i,j) \leq \varepsilon$.
- **Atributos dos nós**: $(x, y), v_i, \theta_i, b_i$
- **Função objetivo (FO1)** usada na heurística gulosa:

\[
\text{FO}_1(C) = \sum_{k=1}^K \left( \min_{i \in C_k} v_i \right) \cdot |C_k|
\]

- **Restrição de compatibilidade**:
\[
|v_i - v_j| \leq f(d_{ij}), \forall (i,j) \in E, \ i,j \in C_k
\]

---

## 🔎 Por que é NP-Difícil?

- A decisão dos clusters envolve variáveis contínuas (velocidade), estrutura topológica (grafo) e restrições combinatórias.
- Reduz a problemas conhecidos como: **Graph Partitioning**, **Clustering with Constraints**, **Max-Min Optimization**.

---

## ⚙️ Heurísticas Aplicadas

| Tipo             | Arquivo                  | Status   |
|------------------|--------------------------|----------|
| Guloso (FO1)     | `guloso_fo1.py`          | ✅ Feito |
| Otimização local | `local_search.py`        | 🔄 Em breve |
| Metaheurística   | `metaheuristica.py`      | 🔄 Em breve (PSO / SA) |

---

## 🧪 Pipeline

### 1. Geração de Dados (src/generate/gerar_dados.py)

- **Distribuição urbana** baseada em `Perlin Noise`
- **Atributos simulados**:
  - $v_i \sim \mathcal{N}(30, 5)$
  - $\theta \sim \mathcal{U}(0, 2\pi)$
  - $b_i \sim \mathcal{U}(20, 100)$

Visualizações geradas automaticamente:
- `hist_velocidade.png`
- `hist_bateria.png`
- `heatmap_densidade.png`
- `posicoes_velocidade.png`

---

### 2. Construção do Grafo (src/graph/construir_grafo.py)

- Método: **ε-ball graph** com $\varepsilon = 50$
- Implementado com **KDTree** (O(n log n))
- Arestas armazenam distância euclidiana

Saídas:
- `grafo_epsilon.graphml`
- `grafo_epsilon_arestas.csv`
- `grafo_epsilon.png`
- `grafo_epsilon_hist_peso.png`
- `grafo_epsilon_hist_grau.png`

---

### 3. Clusterizações Base

Usadas como comparação e input do consenso médio:

| Algoritmo     | Atributos Considerados    |
|---------------|----------------------------|
| KMeans        | Vetoriais (x, y, v, b)     |
| Louvain       | Topologia do grafo         |
| Spectral      | Laplaciano + KMeans        |
| Agglomerativo | Distância hierárquica      |

Salvos em `data/cluster/[algoritmo]/`.

---

### 4. Consenso Médio

- Gera grafo de coocorrência com pesos $w_{ij} \in [0,1]$
- Clusters consensuais construídos por algoritmo **guloso**
- Suporte para aplicar heurísticas sobre esse grafo

---

### 5. Aplicação da FO1 (Guloso)

- Algoritmo explora os nós do grafo original
- Cria agrupamentos conectados que respeitam $\Delta v \leq 5$
- Otimiza a FO1 para formar clusters coesos e seguros

---

## 📊 Resultados Obtidos

- Com 10.000 robôs e cidade de $3000 \times 3000$:
  - FO1 ≈ 58.000
  - Clusters: ~1200
  - Tempo: 0.20s
  - Arestas no grafo: ~200k
  - Grafo esparso e bem distribuído

---

## 📚 Instâncias de Comparação

| Nome        | Origem      | Tamanho | Uso                        |
|-------------|-------------|---------|-----------------------------|
| reddit_5k   | PapersWithCode | 5.000 | Ground truth (subreddits)  |
| roadNet-CA  | SNAP Stanford | 2M     | Malha viária real (em breve) |
| robos.npy   | Sintético   | 10.000  | Instância principal         |

---

## 🔮 Extensão Futuras (Coordenação Real)

- No futuro, pretende-se transformar o grafo em **dinâmico**:
  - Atualizando posições e velocidades
  - Simulando movimentação real com aceleração e missão
  - Incorporando priorização e comunicação assíncrona

---

## 🔧 Parâmetros Globais (config.py)

```python
NUM_ROBOS = 10000
TAMANHO_CIDADE = 3000
RAIO_COMUNICACAO = 50
MODO_GERACAO = 'densidade_realista'
SEED = 42
```

---

## 📝 Versões

- `v0.1`: Heurística gulosa com FO1, geração completa e baseline pronto
- `v0.2+`: Esperado: busca local, metaheurística, benchmark real

---

## Ambientes e Dependências

O projeto utiliza um ambiente virtual Python com as seguintes dependências principais:

- `numpy` — manipulação numérica de matrizes e vetores.
- `scipy` — ferramentas científicas (cKDTree, otimizações).
- `networkx` — manipulação de grafos.
- `matplotlib`, `seaborn` — visualizações e gráficos.
- `scikit-learn` — algoritmos de clusterização e PCA.
- `tqdm` — barra de progresso para loops demorados.

Para reprodutibilidade, o ambiente pode ser recriado via:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📌 Conclusão

Este projeto estabelece uma base sólida para testar **estratégias de clusterização heurística em problemas NP-difíceis** com restrições topológicas. Ele combina:

- Simulação urbana realista
- Geração escalável
- Grafos esparsos conectados
- Funções objetivo interpretáveis
- Visualizações e comparações automatizadas

Ele também conecta diretamente com aplicações reais, como **coordenação urbana de veículos autônomos**, fornecendo um ambiente de teste rigoroso para heurísticas e algoritmos distribuídos.

```

---


### 3.1 Correlação Realista entre Velocidade e Densidade (Atualização v0.3)

Na versão `v0.3` do projeto, a atribuição de velocidade passou a ser modelada de forma mais realista, refletindo o impacto da densidade urbana sobre a movimentação dos robôs. Em vez de usar uma distribuição normal simples, a nova abordagem utiliza a densidade espacial estimada por Perlin Noise para modular a velocidade \( v_i \) de cada robô:

\[
v_i = \text{clip}\left(30 - 10 \cdot \rho(x_i) + \mathcal{N}(0, 5),\ 10,\ 50\right)
\]

Onde:
- \( \rho(x_i) \in [0, 1] \) é a densidade local normalizada obtida a partir do mapa Perlin+Gauss.
- O termo \( -10 \cdot \rho(x_i) \) simula a redução de velocidade em áreas urbanas congestionadas.
- O ruído gaussiano \( \mathcal{N}(0, 5) \) adiciona variabilidade individual ao comportamento de cada robô.
- A função `clip` limita a velocidade a um intervalo físico plausível \([10,\ 50]\) m/s.

#### 🎯 Motivação
Essa mudança tem como objetivo garantir que robôs em regiões mais densas — que simulam centros urbanos ou interseções de tráfego — se movam mais lentamente, conforme esperado em cenários reais. Tal correlação reforça a verossimilhança da simulação e melhora a complexidade do problema de clusterização com restrições, já que os atributos relevantes (como velocidade) deixam de ser independentes da estrutura espacial.

#### ✅ Benefícios
- Gera instâncias **mais desafiadoras** e **coerentes com a realidade urbana**.
- Ajuda a **ampliar o desbalanceamento de clusters**, fundamental para testar heurísticas.
- Facilita a análise de algoritmos sob **restrições de conectividade e atributos correlacionados**.



Construção Avançada do Grafo ε‑ball e Visualizações
A partir dos dados gerados (robôs com atributos de posição, velocidade, bateria), é construído um grafo de visibilidade por raio 
𝜀
ε, conectando robôs que estão a uma distância euclidiana menor que 
𝜀
ε.

🔁 Ajuste Dinâmico do Raio
Para garantir conectividade do grafo:

O raio 
𝜀
ε é inicializado com um valor sugerido (ex: 50 unidades).

Um loop automático aumenta 
𝜀
ε em 10% até que o grafo fique conexo (ou atinja um limite superior).

Isso evita componentes isoladas e garante validade do grafo para os algoritmos de clusterização.

🎯 Visualizações Geradas
Para facilitar análise estrutural e visual do grafo:

Grafo Amostrado com Arestas (grafo_amostra.png):
Subconjunto de 1000 nós com arestas renderizadas em cinza translúcido.

Heatmap de Arestas (heatmap_arestas.png):
Mapa de densidade 2D baseado na concentração de conexões.

Coloração por Velocidade (grafo_velocidade.png):
Nós coloridos de acordo com a velocidade atribuída, usando escala contínua viridis.

Histograma de Grau (degree_hist.png):
Frequência de graus dos nós, indicando distribuição local de conectividade.

Matriz de Adjacência (subgrafo) (adj_matrix.png):
Visualização da conectividade binária dos 200 primeiros nós.

📄 Estatísticas do Grafo
Armazenadas no stats.txt, incluindo:

Número de nós/arestas.

Grau médio, mínimo e máximo.

Densidade do grafo.

Número de componentes conexas (idealmente 1).

