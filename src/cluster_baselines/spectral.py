import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import SpectralClustering


def carregar_grafo(tipo, instancia):
    if tipo == "sintetico":
        grafo_path = f"data/grafo/epsilon_50.0_{instancia}_seed42/grafo.graphml"
    else:
        grafo_path = "data/grafo/roadnet_ca/grafo.graphml"

    if not os.path.exists(grafo_path):
        raise FileNotFoundError(f"Arquivo de grafo não encontrado: {grafo_path}")

    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        for attr in ['x', 'y', 'vel']:
            G.nodes[n][attr] = float(G.nodes[n][attr])
    return G


def aplicar_spectral(G):
    A = nx.to_numpy_array(G)
    n_clusters = 5
    model = SpectralClustering(n_clusters=n_clusters, affinity='precomputed', assign_labels='kmeans', random_state=42)
    labels = model.fit_predict(A)
    return labels


def salvar_resultados(G, labels, tipo, instancia):
    pasta_saida = f"data/baselines/spectral_{tipo}_{instancia}"
    os.makedirs(pasta_saida, exist_ok=True)

    np.save(os.path.join(pasta_saida, "labels.npy"), labels)

    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    plt.figure(figsize=(6, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, s=5)
    plt.title("Spectral Clustering")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "scatter.png"))
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", required=True, choices=["sintetico", "real"])
    parser.add_argument("--instancia", required=True)
    args = parser.parse_args()

    G = carregar_grafo(args.tipo, args.instancia)
    labels = aplicar_spectral(G)
    salvar_resultados(G, labels, args.tipo, args.instancia)


if __name__ == "__main__":
    main()
