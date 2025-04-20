import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain  # pip install python-louvain

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
grafo_path = os.path.join(base_dir, 'data', 'grafo', 'grafo_area_maior.graphml')
saida_dir = os.path.join(base_dir, 'data', 'cluster', 'louvain')
os.makedirs(saida_dir, exist_ok=True)

G = nx.read_graphml(grafo_path)
G = nx.convert_node_labels_to_integers(G)  # garante nós numerados de 0 a N-1

# Louvain
print("[Louvain] Rodando detecção de comunidades...")
partition = community_louvain.best_partition(G)
labels = np.array([partition[i] for i in range(len(partition))])

np.save(os.path.join(saida_dir, 'louvain_labels.npy'), labels)

pos = {i: (float(G.nodes[i]['x']), float(G.nodes[i]['y'])) for i in G.nodes}
plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_color=labels, node_size=25, cmap='tab10', with_labels=False, edge_color='lightgray')
plt.title("Louvain - Clusterização dos Robôs (grafo de conectividade)")
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'louvain_clusters.png'))
plt.close()

with open(os.path.join(saida_dir, 'louvain_resumo.txt'), 'w', encoding='utf-8') as f:
    f.write("Clusterização Louvain - Grafo dos Robôs\n\n")
    f.write(f"Nós: {G.number_of_nodes()}\n")
    f.write(f"Arestas: {G.number_of_edges()}\n")
    unique, counts = np.unique(labels, return_counts=True)
    for u, c in zip(unique, counts):
        f.write(f"Cluster {u}: {c} nós\n")

print("[Louvain] Concluído e arquivos salvos.")
