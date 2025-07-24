#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.colors import Normalize
from matplotlib import cm
import shutil
import time

# Atualização para suportar instâncias até 10000 robôs
NUM_ROBOS = {
    "small": 100,
    "medium": 500,
    "large": 1000,
    "xlarge": 5000,
    "xxlarge": 10000,
}
SEED = 42
RAIO_COMUNICACAO = 50

def print_header(instancia):
    print("\n" + "=" * 60)
    print("  CONSTRUÇÃO DO GRAFO ε-BALL")
    print(f"  Instância: {instancia}")
    print(f"  Quantidade: {NUM_ROBOS[instancia]} robôs")
    print(f"  Seed: {SEED} | Raio inicial: {RAIO_COMUNICACAO}")
    print("=" * 60 + "\n")

def print_footer(grafo_dir, tempo_total, stats):
    print("\n" + "=" * 60)
    print("  GRAFO CONSTRUÍDO COM SUCESSO")
    print(f"  Caminho: {grafo_dir}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  Tempo total: {tempo_total:.4f} segundos")
    print("=" * 60 + "\n")

def construir_grafo_epsilon_ball(num_robos, seed, raio, raio_max=200, passo=1.1, instancia=None):
    t0 = time.time()

    pasta_base = f"data/sinteticos/robos_{num_robos}_seed{seed}"
    grafo_dir  = f"data/grafo/epsilon_{raio:.1f}_{num_robos}_seed{seed}"
    os.makedirs(grafo_dir, exist_ok=True)

    print("[1/7] Carregando dados dos robôs...")
    estados = np.load(os.path.join(pasta_base, "robos.npy"))
    posicoes = estados[:, :2]
    velocidades = estados[:, 2]

    print("[2/7] Construindo grafo ε-ball...")
    tree = KDTree(posicoes)
    atual = raio
    while True:
        pares = tree.query_pairs(r=atual)
        G = nx.Graph()
        G.add_nodes_from(range(num_robos))
        for i in range(num_robos):
            x, y, v, theta, bat = estados[i]
            G.nodes[i].update(x=x, y=y, vel=v, theta=theta, bat=bat)
        for i, j in pares:
            d = np.linalg.norm(posicoes[i] - posicoes[j])
            G.add_edge(i, j, weight=d)
        comps = nx.number_connected_components(G)
        if comps == 1 or atual >= raio_max:
            break
        atual *= passo

    print("[3/7] Salvando arquivos do grafo...")
    nx.write_graphml(G, os.path.join(grafo_dir, "grafo.graphml"))
    with open(os.path.join(grafo_dir, "edges.csv"), "w") as f:
        f.write("source,target,weight\n")
        for u, v, d in G.edges(data=True):
            f.write(f"{u},{v},{d['weight']:.4f}\n")

    print("[4/7] Calculando estatísticas...")
    graus = [d for _, d in G.degree()]
    maior_comp = max(len(c) for c in nx.connected_components(G))
    stats = {
        "n_nodes": num_robos,
        "n_edges": G.number_of_edges(),
        "final_ε": f"{atual:.4f}",
        "components": comps,
        "largest_component_size": maior_comp,
        "avg_degree": f"{np.mean(graus):.2f}",
        "min_degree": np.min(graus),
        "max_degree": np.max(graus),
    }
    with open(os.path.join(grafo_dir, "stats.txt"), "w") as f:
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")

    print("[5/7] Gerando visualizações...")
    pos_dict = {i: (estados[i, 0], estados[i, 1]) for i in range(num_robos)}

    amostra = list(G.nodes)[:1000]
    Gs = G.subgraph(amostra)
    pos_s = {i: pos_dict[i] for i in amostra}
    plt.figure(figsize=(8,6))
    nx.draw(Gs, pos_s, node_size=5, edge_color="gray", width=0.2, alpha=0.4)
    plt.title("Grafo ε-ball (amostra 1k nós)")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grafo_amostra.png"), dpi=300)
    plt.close()

    norm = Normalize(vmin=np.min(velocidades), vmax=np.max(velocidades))
    cmap = cm.viridis
    node_colors = [cmap(norm(G.nodes[i]["vel"])) for i in G.nodes]
    fig, ax = plt.subplots(figsize=(8,6))
    nx.draw(G, pos_dict, node_size=5, node_color=node_colors,
            edge_color="gray", alpha=0.05, width=0.01, ax=ax)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Velocidade")
    plt.title("Grafo ε-ball — nós coloridos por velocidade")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grafo_velocidade.png"), dpi=300)
    plt.close(fig)

    midx, midy = [], []
    for u, v in G.edges():
        x1, y1 = pos_dict[u]
        x2, y2 = pos_dict[v]
        midx.append((x1+x2)/2)
        midy.append((y1+y2)/2)
    plt.figure(figsize=(6,6))
    plt.hist2d(midx, midy, bins=150, cmap="hot")
    plt.colorbar(label="contagem de arestas")
    plt.title("Heatmap de densidade de arestas")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "heatmap_arestas.png"), dpi=300)
    plt.close()

    plt.figure(figsize=(6,4))
    plt.hist(graus, bins=30, edgecolor="black")
    plt.xlabel("Grau")
    plt.ylabel("Número de nós")
    plt.title("Histograma de Grau")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grau_hist.png"))
    plt.close()

    print("[6/7] Copiando robos.npy...")
    shutil.copy(os.path.join(pasta_base, "robos.npy"), os.path.join(grafo_dir, "robos.npy"))

    tempo_total = time.time() - t0
    print_footer(grafo_dir, tempo_total, stats)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--instancia", choices=list(NUM_ROBOS.keys()), required=True)
    parser.add_argument("--tipo", choices=["sintetico", "real"], default="sintetico")
    args = parser.parse_args()

    if args.tipo == "real":
        print("[AVISO] Ignorando construção de grafo para dados reais.")
        sys.exit(0)

    print_header(args.instancia)
    num = NUM_ROBOS[args.instancia]
    construir_grafo_epsilon_ball(num_robos=num, seed=SEED, raio=RAIO_COMUNICACAO, instancia=args.instancia)
