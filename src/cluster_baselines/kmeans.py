import os
import sys
import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from datetime import datetime

# Caminhos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
np.random.seed(42)

# Funções auxiliares
def gerar_labels(clusters, total_n):
    labels = np.full(total_n, -1)
    for i, cluster in enumerate(clusters):
        for node in cluster:
            labels[int(node)] = i
    return labels

def scatter_clusters(G, clusters, path):
    labels = gerar_labels(clusters, len(G.nodes))
    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    plt.figure(figsize=(6, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, s=5)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def salvar_saida(G, clusters, tipo, instancia):
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta = os.path.join("data/cluster_baselines", f"{tipo}_{instancia}_kmeans_{dt}")
    os.makedirs(pasta, exist_ok=True)

    labels = gerar_labels(clusters, len(G.nodes))
    np.save(os.path.join(pasta, "labels.npy"), labels)
    with open(os.path.join(pasta, "resumo.txt"), "w") as f:
        f.write(f"Clusters: {len(clusters)}\n")
    scatter_clusters(G, clusters, os.path.join(pasta, "scatter.png"))
    return pasta

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", choices=["small", "medium", "large", "ca"], required=True)
    args = parser.parse_args()

    # Caminho do grafo
    if args.tipo == "sintetico":
        grafo_path = os.path.join(ROOT, f"data/grafo/epsilon_50.0_{grafo_size(args.instancia)}_seed42/grafo.graphml")
    else:
        grafo_path = os.path.join(ROOT, "data/grafo/roadnet_ca/grafo.graphml")

    # Carregar grafo
    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        G.nodes[n]['x'] = float(G.nodes[n]['x'])
        G.nodes[n]['y'] = float(G.nodes[n]['y'])

    # Extrair posições
    X = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    n_clusters = max(2, int(len(G.nodes)**0.5 // 2))  # Heurística para número de clusters

    # Rodar KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto').fit(X)
    clusters = [[] for _ in range(n_clusters)]
    for node, label in zip(G.nodes, kmeans.labels_):
        clusters[label].append(node)

    outdir = salvar_saida(G, clusters, args.tipo, args.instancia)
    print(f"[KMEANS] Clusters: {n_clusters} | Saída em: {outdir}")

def grafo_size(instancia):
    return {"small": 100, "medium": 500, "large": 1000}[instancia]

if __name__ == "__main__":
    main()
