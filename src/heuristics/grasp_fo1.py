#!/usr/bin/env python3
import os
import sys
import time
import argparse
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from random import seed, shuffle, sample

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from config import NUM_ROBOS, DELTA_V, SEED

def print_header(args):
    print("\n" + "=" * 60)
    print("  EXECUÇÃO GRASP")
    print(f"  Tipo:      {args.tipo}")
    print(f"  Instância: {args.instancia}")
    print(f"  Iterações: {args.max_iter} | α-base = {args.alpha}")
    print("=" * 60 + "\n")

def construir_clusters_guloso(G, alpha=0.4):
    nos_nao_alocados = set(G.nodes)
    clusters = []

    while nos_nao_alocados:
        semente = nos_nao_alocados.pop()
        cluster = [semente]
        fila = [semente]
        vel_min = G.nodes[semente]['vel']
        vel_max = G.nodes[semente]['vel']

        while fila:
            atual = fila.pop(0) 
            vizinhos = list(G.neighbors(atual))
            candidatos = []

            for v in vizinhos:
                if v in nos_nao_alocados:
                    vel_v = G.nodes[v]['vel']
                    if abs(vel_v - vel_min) <= DELTA_V and abs(vel_v - vel_max) <= DELTA_V:
                        ganho = -abs(vel_v - G.nodes[atual]['vel'])
                        candidatos.append((v, ganho, vel_v))

            if candidatos:
                candidatos.sort(key=lambda x: x[1], reverse=True)
                max_ganho = candidatos[0][1]
                min_ganho = candidatos[-1][1]
                limiar = max_ganho - alpha * (max_ganho - min_ganho)
                RCL = [(v, vel) for v, g, vel in candidatos if g >= limiar]

                escolhido_node, escolhido_vel = sample(RCL, 1)[0]
                cluster.append(escolhido_node)
                fila.append(escolhido_node)
                nos_nao_alocados.remove(escolhido_node)

                vel_min = min(vel_min, escolhido_vel)
                vel_max = max(vel_max, escolhido_vel)
                

        clusters.append(cluster)

    return clusters


def mover_vizinho(G, clusters, busca="first", max_local=50):
    def esta_conectado(G, nodes):
        return nx.is_connected(G.subgraph(nodes)) if len(nodes) > 1 else True

    min_vel = [min(G.nodes[n]['vel'] for n in c) if c else 0 for c in clusters]
    tam = [len(c) for c in clusters]
    fo_atual = sum(m * t for m, t in zip(min_vel, tam))

    sem_melhora = 0
    iter_local = 0

    while iter_local < max_local and sem_melhora < 10:
        melhor_delta = 0
        melhor_mov = None

        for cid_from, c_from in enumerate(clusters):
            if len(c_from) <= 1:
                continue
            for n in list(c_from):
                c_from_test = [x for x in c_from if x != n]
                if not esta_conectado(G, c_from_test):
                    continue

                v_n = G.nodes[n]['vel']
                for cid_to, c_to in enumerate(clusters):
                    if cid_from == cid_to:
                        continue
                    
                    if not all(abs(v_n - G.nodes[v]['vel']) <= DELTA_V for v in c_to):
                        continue

                    novo_t_from = len(c_from) - 1
                    novo_min_from = min(G.nodes[x]['vel'] for x in c_from_test) if G.nodes[n]['vel'] == min_vel[cid_from] else min_vel[cid_from]
                    novo_t_to = len(c_to) + 1
                    novo_min_to = min(min_vel[cid_to], v_n) if c_to else v_n

                    delta = (novo_min_from * novo_t_from + novo_min_to * novo_t_to) - (min_vel[cid_from] * len(c_from) + min_vel[cid_to] * len(c_to))

                    if delta > melhor_delta:
                        melhor_delta = delta
                        melhor_mov = (cid_from, cid_to, n)

                        if busca == "first":
                            break
                if melhor_mov and busca == "first":
                    break
            if melhor_mov and busca == "first":
                break

        if melhor_mov:
            cid_from, cid_to, n = melhor_mov
            clusters[cid_from].remove(n)
            clusters[cid_to].append(n)
            sem_melhora = 0
            min_vel[cid_from] = min(G.nodes[x]['vel'] for x in clusters[cid_from]) if clusters[cid_from] else 0
            min_vel[cid_to] = min(G.nodes[x]['vel'] for x in clusters[cid_to])
            tam[cid_from] -= 1
            tam[cid_to] += 1
            fo_atual += melhor_delta
        else:
            sem_melhora += 1

        iter_local += 1

    return clusters, fo_atual


def salvar_saida(G, clusters, fo1, tempo, tipo, instancia, alpha, iteracao, output_dir):
    nome = f"{tipo}_{instancia}_grasp_iter{iteracao}_a{alpha}"
    pasta = os.path.join(output_dir, nome)
    os.makedirs(pasta, exist_ok=True)

    with open(os.path.join(pasta, "refinamento_resumo.txt"), "w") as f:
        f.write(f"Clusters: {len(clusters)}\n")
        f.write(f"FO1: {fo1:.2f}\n")
        f.write(f"Tempo: {tempo:.2f} s\n")

    labels = {str(n): -1 for n in G.nodes}
    for cid, cluster in enumerate(clusters):
        for n in cluster:
            labels[str(n)] = cid

    with open(os.path.join(pasta, "labels.npy"), "wb") as f:
        np.save(f, labels, allow_pickle=True)
    with open(os.path.join(pasta, "clusters.pkl"), "wb") as f:
        pickle.dump(clusters, f)

    return pasta

def carregar_grafo(tipo, instancia):
    if tipo == 'sintetico':
        pasta = f"data/grafo/epsilon_50.0_{NUM_ROBOS[instancia]}_seed{SEED}"
        grafo_path = os.path.join(ROOT, pasta, "grafo.graphml")
    else:
        grafo_path = os.path.join(ROOT, "data/grafo/roadnet_ca", "grafo.graphml")

    G = nx.read_graphml(grafo_path)
    for n in G.nodes:
        for attr in ["x", "y", "vel", "theta", "bat"]:
            G.nodes[n][attr] = float(G.nodes[n][attr])
    return G

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", choices=["small", "medium", "large", "xlarge", "xxlarge", "real"], required=True)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--max_iter", type=int, default=100)
    parser.add_argument("--max_local", type=int, default=50)
    parser.add_argument("--busca", choices=["first", "best"], default="first")
    parser.add_argument("--output_dir", default=os.path.join(ROOT, "data", "grasp"))
    args = parser.parse_args()

    print_header(args)

    G = carregar_grafo(args.tipo, args.instancia)
    melhor_fo = -1
    melhor_clusters = None
    total_time = 0

    for i in range(1, args.max_iter + 1):
        t0 = time.time()
        seed(SEED + i)

        clusters = construir_clusters_guloso(G, alpha=args.alpha)
        clusters, fo = mover_vizinho(G, clusters, busca=args.busca, max_local=args.max_local)
        tempo_iter = time.time() - t0
        total_time += tempo_iter

        print(f"[Iteração {i:02d}] FO₁ = {fo:.2f} | Δ = {fo - melhor_fo:.4f} | Tempo acumulado = {total_time:.4f}s")

        if fo > melhor_fo:
            melhor_fo = fo
            melhor_clusters = [c.copy() for c in clusters]
            outdir = salvar_saida(G, melhor_clusters, melhor_fo, total_time, args.tipo, args.instancia, args.alpha, i, args.output_dir)

    print(f"\nMelhor FO₁: {melhor_fo:.2f} salvo em {outdir}")

if __name__ == "__main__":
    main()
