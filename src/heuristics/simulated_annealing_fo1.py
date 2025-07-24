#!/usr/bin/env python3
import sys, os, time, math, random, argparse, pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)

from config import SEED, NUM_ROBOS, DELTA_V

MAX_ITER = 1500
INITIAL_TEMPERATURE = 1000
ALPHA = 0.97
STOP_NO_IMPROVE = 300
OUTPUT_DIR = "data/sa_results"
random.seed(SEED)


def print_header(tipo, instancia):
    print("\n===== SIMULATED ANNEALING FO₁ =====")
    print(f"Tipo: {tipo} | Instância: {instancia}")


def print_iter(i, fo, best, T):
    print(f"[Iter {i}] FO₁ = {fo:.2f} | Melhor = {best:.2f} | T = {T:.2f}")


def calcular_fo1(G, clusters):
    return sum(min(G.nodes[n]['vel'] for n in c) * len(c) for c in clusters if c)


def carregar_instancia(tipo, instancia):
    if tipo == 'sintetico':
        pasta = f"data/grafo/epsilon_50.0_{NUM_ROBOS[instancia]}_seed{SEED}"
        grafo_path = os.path.join(pasta, "grafo.graphml")
    else:
        grafo_path = os.path.join("data", "grafo", "roadnet_ca", "grafo.graphml")

    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        for attr in ['x', 'y', 'vel', 'theta', 'bat']:
            G.nodes[n][attr] = float(G.nodes[n][attr])
    return G

def salvar_saida(G, clusters, fo, tempo, tipo, instancia):
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta = os.path.join(OUTPUT_DIR, f"{tipo}_{instancia}_SA_{dt}")
    os.makedirs(pasta, exist_ok=True)

    np.save(os.path.join(pasta, "labels.npy"), gerar_labels(G, clusters))
    pickle.dump(clusters, open(os.path.join(pasta, "clusters.pkl"), "wb"))
    with open(os.path.join(pasta, "sa_resumo.txt"), "w") as f:
        f.write(f"FO₁ final: {fo:.2f}\nTempo: {tempo:.2f}s\nClusters: {len(clusters)}\n")

    scatter_clusters(G, clusters, os.path.join(pasta, "scatter.png"))
    return pasta


def gerar_labels(G, clusters):
    labels = np.full(len(G.nodes), -1)
    for cid, c in enumerate(clusters):
        for n in c:
            labels[int(n)] = cid
    return labels


def scatter_clusters(G, clusters, path):
    labels = gerar_labels(G, clusters)
    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    plt.figure(figsize=(6, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, s=5)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def simulated_annealing(G):
    from grasp_fo1 import construir_clusters_guloso  

    def calcular_delta(G, clusters, cid_from, cid_to, n):
        v_n = G.nodes[n]['vel']

        c_from = clusters[cid_from]
        c_to = clusters[cid_to]

        tam_from = len(c_from)
        tam_to = len(c_to)

        vel_from = [G.nodes[x]['vel'] for x in c_from]
        vel_to = [G.nodes[x]['vel'] for x in c_to]

        min_from = min(vel_from)
        min_to = min(vel_to) if vel_to else float('inf')

        vel_from_restante = [v for x, v in zip(c_from, vel_from) if x != n]
        novo_min_from = min(vel_from_restante) if vel_from_restante else 0
        novo_tam_from = tam_from - 1

        novo_min_to = min(min_to, v_n)
        novo_tam_to = tam_to + 1

        fo_antiga = min_from * tam_from + min_to * tam_to
        fo_nova = novo_min_from * novo_tam_from + novo_min_to * novo_tam_to

        return fo_nova - fo_antiga

    atual_clusters = construir_clusters_guloso(G)
    atual_fo = calcular_fo1(G, atual_clusters)

    best_clusters = [c.copy() for c in atual_clusters]
    best_fo = atual_fo

    T = INITIAL_TEMPERATURE
    iter = 0
    no_improve = 0

    print_iter(iter, atual_fo, best_fo, T)

    while iter < MAX_ITER and no_improve < STOP_NO_IMPROVE:
        iter += 1

        try:
            cid_from, c_from = random.choice([(i, c) for i, c in enumerate(atual_clusters) if len(c) > 1])
            n_movido = random.choice(c_from)
            cid_to = random.choice([i for i in range(len(atual_clusters)) if i != cid_from])
        except IndexError:
            continue

        c_from_restante = [x for x in c_from if x != n_movido]
        if c_from_restante and not nx.is_connected(G.subgraph(c_from_restante)):
            continue

        c_to = atual_clusters[cid_to]
        v_n = G.nodes[n_movido]['vel']
        if not all(abs(v_n - G.nodes[v]['vel']) <= DELTA_V for v in c_to):
            continue

        delta = calcular_delta(G, atual_clusters, cid_from, cid_to, n_movido)

        if delta > 0 or random.random() < math.exp(delta / T):
            atual_clusters[cid_from].remove(n_movido)
            atual_clusters[cid_to].append(n_movido)
            atual_fo += delta

        if atual_fo > best_fo:
            best_clusters = [c.copy() for c in atual_clusters]
            best_fo = atual_fo
            no_improve = 0
        else:
            no_improve += 1

        T *= ALPHA
        print_iter(iter, atual_fo, best_fo, T)

    return best_clusters, best_fo



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", choices=list(NUM_ROBOS.keys()), required=True)
    args = parser.parse_args()

    print_header(args.tipo, args.instancia)
    G = carregar_instancia(args.tipo, args.instancia)
    start = time.time()
    clusters, fo = simulated_annealing(G)
    tempo = time.time() - start
    outdir = salvar_saida(G, clusters, fo, tempo, args.tipo, args.instancia)

    print("\n======= RESULTADO FINAL =======")
    print(f"FO₁ final: {fo:.2f}")
    print(f"Tempo: {tempo:.2f}s")
    print(f"Clusters: {len(clusters)}")
    print(f"Saída em: {outdir}")


if __name__ == "__main__":
    main()
