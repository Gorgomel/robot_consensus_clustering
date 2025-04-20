import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
dados_path = os.path.join(base_dir, 'data', 'sinteticos', 'robos.npy')
saida_dir = os.path.join(base_dir, 'data', 'cluster', 'aglomerativo')
os.makedirs(saida_dir, exist_ok=True)

robos = np.load(dados_path)
X = robos  # usa todas as 5 features: x, y, v, θ, bateria

n_clusters = 5
modelo = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
labels = modelo.fit_predict(X)

np.save(os.path.join(saida_dir, 'agglomerativo_labels.npy'), labels)

plt.figure(figsize=(8, 6))
scatter = plt.scatter(robos[:, 0], robos[:, 1], c=labels, cmap='tab10', s=30)
plt.colorbar(scatter, label='Cluster Agglomerativo')
plt.xlabel('Posição X')
plt.ylabel('Posição Y')
plt.title(f'Agglomerativo - Clusterização dos Robôs (k={n_clusters})')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'agglomerativo_clusters.png'))
plt.close()

with open(os.path.join(saida_dir, 'agglomerativo_resumo.txt'), 'w', encoding='utf-8') as f:
    f.write("Clusterização Aglomerativa - Dados Sintéticos\n\n")
    f.write(f"Número de robôs: {len(robos)}\n")
    f.write(f"Número de clusters: {n_clusters}\n")
    unique, counts = np.unique(labels, return_counts=True)
    for u, c in zip(unique, counts):
        f.write(f"Cluster {u}: {c} elementos\n")

print("Clusterização aglomerativa concluída e arquivos salvos.")
