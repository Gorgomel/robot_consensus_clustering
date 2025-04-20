import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
grafo_path = os.path.join(base_dir, 'data', 'grafo', 'grafo_area_maior.graphml')
saida_dir = os.path.join(base_dir, 'data', 'cluster', 'spectral')
os.makedirs(saida_dir, exist_ok=True)

G = nx.read_graphml(grafo_path)
G = nx.convert_node_labels_to_integers(G)
adj_matrix = nx.to_numpy_array(G)

n_clusters = 5
modelo = SpectralClustering(n_clusters=n_clusters, affinity='precomputed', assign_labels='kmeans', random_state=42)
labels = modelo.fit_predict(adj_matrix)

np.save(os.path.join(saida_dir, 'spectral_labels.npy'), labels)

pos = {i: (float(G.nodes[i]['x']), float(G.nodes[i]['y'])) for i in G.nodes}

plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_color=labels, node_size=25, cmap='tab10', with_labels=False, edge_color='lightgray')
plt.title(f"Spectral Clustering - Robôs com base no grafo (k={n_clusters})")
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'spectral_clusters.png'))
plt.close()

with open(os.path.join(saida_dir, 'spectral_resumo.txt'), 'w', encoding='utf-8') as f:
    f.write("Clusterização Spectral - Grafo dos Robôs\n\n")
    f.write(f"Nós: {G.number_of_nodes()}\n")
    f.write(f"Arestas: {G.number_of_edges()}\n")
    unique, counts = np.unique(labels, return_counts=True)
    for u, c in zip(unique, counts):
        f.write(f"Cluster {u}: {c} nós\n")

print("Clusterização Spectral concluída e arquivos salvos.")
