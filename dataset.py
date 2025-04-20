import torch
import time
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

from torch_geometric.datasets import Reddit
from torch_geometric.transforms import NormalizeFeatures
from torch_geometric.utils import subgraph

# Carregar e normalizar o dataset Reddit
dataset = Reddit(root='data/Reddit', transform=NormalizeFeatures())
data = dataset[0]

# Parâmetros
n_amostra = 2000  # número de nós na amostra
subset_mask = torch.arange(n_amostra)

# Subgrafo
sub_edge_index, _ = subgraph(subset_mask, data.edge_index, relabel_nodes=True)
sub_x = data.x[subset_mask]
sub_y = data.y[subset_mask]

# Número de clusters baseado nos rótulos únicos da amostra
k = len(torch.unique(sub_y))

# Clusterização com KMeans
start = time.perf_counter()
kmeans = KMeans(n_clusters=k, random_state=0)
predicted_clusters = kmeans.fit_predict(sub_x.numpy())
end = time.perf_counter()
tempo_ms = (end - start) * 1000

# Avaliação com NMI e ARI
nmi = normalized_mutual_info_score(sub_y.numpy(), predicted_clusters)
ari = adjusted_rand_score(sub_y.numpy(), predicted_clusters)

# Criar tabela de resultados
tabela = pd.DataFrame([{
    'Instância': 'Reddit-2k',
    'Num Nós': n_amostra,
    'Solução Referência (NMI)': "1.00 (rótulo)",
    'Solução Gulosa (NMI)': f"{nmi:.4f}",
    'Solução Gulosa (ARI)': f"{ari:.4f}",
    'Tempo (ms)': f"{tempo_ms:.2f}"
}])

# Exibir tabela
print(tabela)
tabela.to_csv("resultado_clusterizacao.csv", index=False)

