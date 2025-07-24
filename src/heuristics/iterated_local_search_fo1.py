#!/usr/bin/env python3
import os
import sys
import time
import random
import argparse
import pickle
import numpy as np
import networkx as nx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

from config import SEED, NUM_ROBOS, DELTA_V
from grasp_fo1 import construir_clusters_guloso, calcular_fo1
from grasp_fo1 import mover_vizinho

ILS_MAX_ITER = 100
ILS_NO_IMPROVE = 50
PERTURB_FORCE = 5
OUTPUT_DIR = os.path.join(ROOT, 'data', 'ils_results')

random.seed(SEED)

def perturbar(G, clusters, força=PERTURB_FORCE):

    S_pert = [c.copy() for c in clusters]
    for _ in range(força):
        try:
            cid_from, c_from = random.choice([(i, c) for i, c in enumerate(S_pert) if len(c) > 1])
            n = random.choice(c_from)
            cid_to = random.choice([i for i in range(len(S_pert)) if i != cid_from])

            restante = [x for x in c_from if x != n]
            if restante and not nx.is_connected(G.subgraph(restante)):
                continue

            v_n = G.nodes[n]['vel']
            if not all(abs(v_n - G.nodes[v]['vel']) <= DELTA_V for v in S_pert[cid_to]):
                continue

            S_pert[cid_from].remove(n)
            S_pert[cid_to].append(n)
        except Exception:
            continue
    return S_pert

def run_ils(G):
    S0 = construir_clusters_guloso(G, alpha=0.1)
    S_best, best_fo = mover_vizinho(G, S0, busca='best')

    S_best_clusters, S_best_fo = S_best, best_fo
    no_improve = 0
    it = 0

    while it < ILS_MAX_ITER and no_improve < ILS_NO_IMPROVE:
        it += 1
      
        S_pert = perturbar(G, S_best_clusters, força=PERTURB_FORCE)
       
        S_nova_clusters, fo_nova = mover_vizinho(G, S_pert, busca='best')
        
        if fo_nova > S_best_fo:
            S_best_clusters = S_nova_clusters
            S_best_fo = fo_nova
            no_improve = 0
        else:
            no_improve += 1
        print(f"[Iter {it}] FO₁ Best = {S_best_fo:.2f} | Novo = {fo_nova:.2f} | no_improve = {no_improve}")

    return S_best_clusters, S_best_fo

def salvar_resultados(G, clusters, fo):
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUTPUT_DIR, f"ILS_{ts}")
    os.makedirs(out, exist_ok=True)
    
    labels = np.full(len(G.nodes), -1)
    for cid, c in enumerate(clusters):
        for n in c:
            labels[int(n)] = cid
    np.save(os.path.join(out, 'labels.npy'), labels)
    pickle.dump(clusters, open(os.path.join(out, 'clusters.pkl'), 'wb'))
    with open(os.path.join(out, 'ils_resumo.txt'), 'w') as f:
        f.write(f"FO₁ final: {fo:.2f}\nClusters: {len(clusters)}\n")
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tipo', choices=['sintetico', 'real'], required=True)
    parser.add_argument('--instancia', choices=list(NUM_ROBOS.keys()), required=True)
    args = parser.parse_args()

   
    if args.tipo == 'sintetico':
        path = os.path.join(ROOT, f"data/grafo/epsilon_50.0_{NUM_ROBOS[args.instancia]}_seed{SEED}", 'grafo.graphml')
    else:
        path = os.path.join(ROOT, 'data', 'roadnet_ca', 'grafo.graphml')
    G = nx.read_graphml(path)
    for n in G.nodes:
        for attr in ['x','y','vel','theta','bat']:
            G.nodes[n][attr] = float(G.nodes[n][attr])

    start = time.time()
    best_clusters, best_fo = run_ils(G)
    outdir = salvar_resultados(G, best_clusters, best_fo)
    elapsed = time.time() - start
    print(f"\nILS Final: FO₁ = {best_fo:.2f} | Tempo = {elapsed:.2f}s | Saída = {outdir}")

if __name__ == '__main__':
    main()
