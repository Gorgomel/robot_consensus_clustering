import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Diretórios
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
cluster_base = os.path.join(base_dir, 'data', 'cluster')
saida_dir = os.path.join(base_dir, 'data', 'coocorrencia')
os.makedirs(saida_dir, exist_ok=True)

# Métodos usados
metodos = ['kmeans', 'agglomerativo', 'louvain', 'spectral']

# Carrega rótulos
rotulos = []
for metodo in metodos:
    caminho = os.path.join(cluster_base, metodo, f'{metodo}_labels.npy')
    rotulos.append(np.load(caminho))

# Número de nós
n = len(rotulos[0])
m = len(rotulos)

# Inicializa matriz de coocorrência
cooc = np.zeros((n, n), dtype=np.float32)

# Para cada método, incrementa os pares (i, j) que aparecem juntos
for labels in rotulos:
    for cluster_id in np.unique(labels):
        indices = np.where(labels == cluster_id)[0]
        for i in indices:
            for j in indices:
                if i != j:
                    cooc[i, j] += 1

# Normaliza
cooc /= m

# Constrói o grafo
G = nx.Graph()
for i in range(n):
    G.add_node(i)

for i in range(n):
    for j in range(i + 1, n):
        if cooc[i, j] > 0:
            G.add_edge(i, j, weight=cooc[i, j])

# Salva grafo
nx.write_graphml(G, os.path.join(saida_dir, 'grafo_coocorrencia.graphml'))
np.save(os.path.join(saida_dir, 'matriz_coocorrencia.npy'), cooc)

# CSV das arestas
with open(os.path.join(saida_dir, 'grafo_coocorrencia_arestas.csv'), 'w', encoding='utf-8') as f:
    f.write('source,target,peso\n')
    for u, v, d in G.edges(data=True):
        f.write(f'{u},{v},{d["weight"]:.3f}\n')

# Visualização
plt.figure(figsize=(10, 8))
edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())
pos = nx.spring_layout(G, seed=42, k=0.15)
nx.draw(G, pos, node_size=15, node_color='skyblue', edge_color=weights,
        edge_cmap=plt.cm.plasma, width=1.5, with_labels=False)
plt.title('Grafo de Coocorrência (baseado em 4 clusterizações)')
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'grafo_coocorrencia.png'))
plt.close()

print(f"Grafo de coocorrência salvo com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")
