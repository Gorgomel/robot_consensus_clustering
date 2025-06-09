#!/usr/bin/env python3
import os
import sys
import time
import argparse
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import logging
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from config import SEED, NUM_ROBOS, DELTA_V


def print_header(args):
    print("\n" + "=" * 60)
    print(f"  EXECUÇÃO INICIADA")
    print(f"  Modo:     {args.modo}")
    print(f"  Tipo:     {args.tipo}")
    print(f"  Instância:{args.instancia}")
    print(f"  Iterações:{args.max_iter}")
    print("=" * 60 + "\n")


def print_iteracao(i, fo1, delta, tempo):
    print(f"[Iteração {i:02d}] FO₁ = {fo1:.2f} | Δ = {delta:.4f} | Tempo acumulado = {tempo:.2f}s")


def print_footer(fo1, tempo_total, clusters, saida):
    print("\n" + "=" * 60)
    print("  EXECUÇÃO FINALIZADA")
    print(f"  Clusters finais: {len(clusters)}")
    print(f"  FO₁ final:        {fo1:.2f}")
    print(f"  Tempo total:      {tempo_total:.2f} segundos")
    print(f"  Resultados em:    {saida}")
    print("=" * 60 + "\n")


def carregar_instancia(tipo, instancia):
    if tipo == 'sintetico':
        pasta = f"data/grafo/epsilon_50.0_{NUM_ROBOS[instancia]}_seed{SEED}"
        grafo_path = os.path.join(ROOT, pasta, "grafo.graphml")
        cluster_path = os.path.join(ROOT, "data", "cluster", f"sintetico_{instancia}_guloso_fo1")
    else:
        pasta = "data/grafo/roadnet_ca"
        grafo_path = os.path.join(ROOT, pasta, "grafo.graphml")
        cluster_path = os.path.join(ROOT, "data", "cluster", "real_guloso_fo1")

    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        for attr in ["x", "y", "vel", "theta", "bat"]:
            G.nodes[n][attr] = float(G.nodes[n][attr])

    with open(os.path.join(cluster_path, "clusters.pkl"), "rb") as f:
        clusters = pickle.load(f)

    exemplo_node = next(iter(G.nodes))
    if isinstance(exemplo_node, str):
        clusters = [[str(n) for n in c] for c in clusters]
    else:
        clusters = [[int(n) for n in c] for c in clusters]

    return G, clusters, tipo, instancia


def mover_vizinho_best(G, clusters, timeout_por_iter=180, max_iter=150):
    iteracao = 0
    tempo_total = 0
    fo1_por_iter = []
    sem_melhora = 0
    sem_melhora_limite = 10

    min_vel = [min(G.nodes[n]['vel'] for n in c) if c else 0 for c in clusters]
    tam = [len(c) for c in clusters]
    fo_atual = sum(m * t for m, t in zip(min_vel, tam))

    while iteracao < max_iter and sem_melhora < sem_melhora_limite:
        iteracao += 1
        t0 = time.time()
        melhor_delta = 0
        melhor_mov = None

        buckets = defaultdict(list)
        for cid, c in enumerate(clusters):
            if not c: continue
            vmin = min_vel[cid]
            bucket_id = int(vmin // DELTA_V)
            buckets[bucket_id].append(cid)

        for cid_from, c_from in enumerate(clusters):
            if len(c_from) <= 1: continue
            for n in list(c_from):
                v_n = G.nodes[n]['vel']
                bucket_ids = range(int(v_n // DELTA_V) - 1, int(v_n // DELTA_V) + 2)
                possiveis = [cid for bid in bucket_ids for cid in buckets[bid] if cid != cid_from]

                for cid_to in possiveis:
                    c_to = clusters[cid_to]
                    if not any(abs(v_n - G.nodes[v]['vel']) <= DELTA_V for v in c_to):
                        continue

                    novo_t_from = tam[cid_from] - 1
                    novo_min_from = min(G.nodes[x]['vel'] for x in c_from if x != n) if v_n == min_vel[cid_from] else min_vel[cid_from]
                    novo_min_to = min(min_vel[cid_to], v_n) if c_to else v_n
                    novo_t_to = tam[cid_to] + 1

                    delta_from = novo_min_from * novo_t_from - min_vel[cid_from] * tam[cid_from]
                    delta_to = novo_min_to * novo_t_to - min_vel[cid_to] * tam[cid_to]
                    delta = delta_from + delta_to

                    if delta > melhor_delta:
                        melhor_delta = delta
                        melhor_mov = (cid_from, cid_to, n, novo_min_from, novo_min_to, novo_t_from, novo_t_to)

        if melhor_mov:
            cid_from, cid_to, n, new_min_from, new_min_to, new_t_from, new_t_to = melhor_mov
            clusters[cid_from].remove(n)
            clusters[cid_to].append(n)
            min_vel[cid_from] = new_min_from
            min_vel[cid_to] = new_min_to
            tam[cid_from] = new_t_from
            tam[cid_to] = new_t_to
            fo_atual += melhor_delta
            sem_melhora = 0
        else:
            sem_melhora += 1

        tempo_iter = time.time() - t0
        tempo_total += tempo_iter
        fo1_por_iter.append(fo_atual)
        print_iteracao(iteracao, fo_atual, melhor_delta, tempo_total)

    return clusters, fo_atual, tempo_total, fo1_por_iter


def salvar_saida(G, clusters, fo1, tempo, tipo, instancia, modo, fo1_iters, output_dir):
    saida = os.path.join(output_dir, f"{tipo}_{instancia}_{modo}")
    os.makedirs(saida, exist_ok=True)

    with open(os.path.join(saida, "refinamento_resumo.txt"), "w") as f:
        f.write(f"Clusters: {len(clusters)}\n")
        f.write(f"FO1: {fo1:.2f}\n")
        f.write(f"Tempo: {tempo:.2f} s\n")

    labels = np.full(len(G.nodes), -1)
    for cid, cluster in enumerate(clusters):
        for n in cluster:
            labels[int(n)] = cid
    np.save(os.path.join(saida, "labels.npy"), labels)
    with open(os.path.join(saida, "clusters.pkl"), "wb") as f:
        pickle.dump(clusters, f)

    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    plt.figure(figsize=(7, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, cmap='tab20', s=5, alpha=0.7)
    plt.title(f"Clusters - Refinamento ({modo})")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.savefig(os.path.join(saida, "scatter_clusters.png"))
    plt.close()

    tamanhos = [len(c) for c in clusters]
    plt.figure()
    plt.hist(tamanhos, bins=30, edgecolor='black', color='blue')
    plt.xlabel("Tamanho do cluster")
    plt.ylabel("Frequência")
    plt.title("Histograma de Tamanhos de Cluster")
    plt.tight_layout()
    plt.savefig(os.path.join(saida, "hist_tamanhos.png"))
    plt.close()

    with open(os.path.join(saida, "refinamento_profiling.txt"), "w") as f:
        f.write(f"Iterações: {len(fo1_iters)}\n")
        f.write(f"FO₁ final: {fo1:.2f}\n")
        f.write(f"Tempo total: {tempo:.2f} s\n")
        f.write("FO₁ por iteração:\n")
        for i, fo in enumerate(fo1_iters, 1):
            f.write(f"  {i}: {fo:.2f}\n")

    return saida


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", choices=list(NUM_ROBOS.keys()))
    parser.add_argument("--modo", choices=["best"], default="best")
    parser.add_argument("--timeout_iter", type=int, default=180)
    parser.add_argument("--max_iter", type=int, default=150)
    parser.add_argument("--output_dir", default=os.path.join(ROOT, "data", "best_improvement"))
    args = parser.parse_args()

    if args.tipo == "sintetico" and not args.instancia:
        parser.error("--instancia é obrigatório para tipo sintetico")

    print_header(args)

    G, clusters_iniciais, tipo, instancia = carregar_instancia(args.tipo, args.instancia or "real")
    clusters = [c.copy() for c in clusters_iniciais]
    t0 = time.time()

    clusters, fo1, tempo_total, fo1_iters = mover_vizinho_best(
        G, clusters,
        timeout_por_iter=args.timeout_iter,
        max_iter=args.max_iter
    )

    pasta_saida = salvar_saida(G, clusters, fo1, tempo_total, tipo, instancia, args.modo, fo1_iters, args.output_dir)
    print_footer(fo1, tempo_total, clusters, pasta_saida)


if __name__ == "__main__":
    main()
