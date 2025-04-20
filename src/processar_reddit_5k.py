import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dados_path = os.path.join(base_dir, 'data', 'Reddit', 'processed', 'reddit_5k.npz')
saida_dir = os.path.join(base_dir, 'data', 'Reddit', 'processed')
os.makedirs(saida_dir, exist_ok=True)

reddit = np.load(dados_path)
x = reddit['feature']
y = reddit['label']
ids = reddit['node_ids']
edge_index = reddit['edge_index']

n_nodes = x.shape[0]

G = nx.Graph()

for i in range(n_nodes):
    G.add_node(i,
               features=','.join(map(str, x[i])),
               label=int(y[i]))

for src, dst in zip(edge_index[0], edge_index[1]):
    G.add_edge(int(src), int(dst))

print(f"Reddit 5k: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
grau_medio = sum(dict(G.degree()).values()) / G.number_of_nodes()
print(f"Grau médio: {grau_medio:.2f}")

nx.write_graphml(G, os.path.join(saida_dir, 'reddit_5k.graphml'))

with open(os.path.join(saida_dir, 'reddit_5k_arestas.csv'), 'w', encoding='utf-8') as f:
    f.write("source,target\n")
    for u, v in G.edges():
        f.write(f"{u},{v}\n")

subG = G.subgraph(list(G.nodes)[:300])
plt.figure(figsize=(10, 10))
nx.draw(subG, node_size=10, node_color='orange', edge_color='gray', with_labels=False)
plt.title("Subgrafo Reddit (300 nós)")
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'reddit_5k_subgrafo.png'))
plt.close()

with open(os.path.join(saida_dir, 'reddit_5k_resumo.txt'), 'w', encoding='utf-8') as f:
    f.write("Resumo do grafo Reddit 5k\n\n")
    f.write(f"Nós: {G.number_of_nodes()}\n")
    f.write(f"Arestas: {G.number_of_edges()}\n")
    f.write(f"Grau médio: {grau_medio:.2f}\n")
    f.write(f"Labels (classes únicas): {len(np.unique(y))}\n")
