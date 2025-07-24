import os
import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
from datetime import datetime


def carregar_grafo(tipo, instancia):
    if tipo == "sintetico":
        grafo_path = f"data/grafo/epsilon_50.0_{instancia}_seed42/grafo.graphml"
    else:
        grafo_path = "data/grafo/roadnet_ca/grafo.graphml"

    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        for attr in ['x', 'y', 'vel']:
            G.nodes[n][attr] = float(G.nodes[n][attr])
    return G


def salvar_resultados(G, particao, tipo, instancia):
    labels = np.array([particao[str(n)] for n in G.nodes])

    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = f"data/baselines/louvain_{tipo}_{instancia}_{dt}"
    os.makedirs(outdir, exist_ok=True)

    np.save(os.path.join(outdir, "louvain_labels.npy"), labels)

    # Scatter
    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    plt.figure(figsize=(6, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, s=5, cmap='tab20')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "louvain_clusters.png"))
    plt.close()

    with open(os.path.join(outdir, "louvain_resumo.txt"), "w") as f:
        f.write(f"Clusters: {len(set(labels))}\n")

    print(f"[LOUVAIN] Resultado salvo em: {outdir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", required=True)
    args = parser.parse_args()

    G = carregar_grafo(args.tipo, args.instancia)
    particao = community_louvain.best_partition(G)
    salvar_resultados(G, particao, args.tipo, args.instancia)
