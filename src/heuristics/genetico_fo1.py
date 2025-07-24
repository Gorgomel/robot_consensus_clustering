#!/usr/bin/env python3
import os
import sys
import time
import random
import argparse
import pickle
import numpy as np
import networkx as nx
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from grasp_fo1 import construir_clusters_guloso
from grasp_fo1 import calcular_fo1  
from config import SEED, NUM_ROBOS, DELTA_V

POP_SIZE = 50
MAX_GEN = 200
TOURNAMENT_K = 3
ELITISM_COUNT = 2
MUTATION_RATE = 0.1
PENALTY_DISCONN = 1e6
PENALTY_DELTA = 1e3

OUTPUT_DIR = os.path.join(ROOT, 'data', 'ga_results')
random.seed(SEED)


def gerar_populacao_inicial(G, pop_size):
    pop = []

    c1 = construir_clusters_guloso(G)
    pop.append(crom_from_clusters(c1))

    c2 = construir_clusters_guloso(G, alpha=0.2)
    pop.append(crom_from_clusters(c2))

    alphas = list(np.linspace(0.1, 0.5, pop_size - 2))
    for a in alphas:
        c = construir_clusters_guloso(G, alpha=a)
        pop.append(crom_from_clusters(c))
    return pop[:pop_size]


def crom_from_clusters(clusters):
    n = sum(len(c) for c in clusters)
    chrom = [0] * n
    for cid, c in enumerate(clusters):
        for node in c:
            chrom[int(node)] = cid
    return chrom


def clusters_from_crom(chrom):
    clusters = defaultdict(list)
    for idx, cid in enumerate(chrom):
        clusters[cid].append(idx)
    return list(clusters.values())


def fitness(chrom, G):
    clusters = clusters_from_crom(chrom)
    fo = calcular_fo1(G, clusters)

    pen = 0
    for c in clusters:
        if len(c) > 1:
            subG = G.subgraph(c)
            if not nx.is_connected(subG):
                pen += PENALTY_DISCONN
            vels = [G.nodes[n]['vel'] for n in c]
            if max(vels) - min(vels) > DELTA_V:
                pen += PENALTY_DELTA
    return fo - pen


def tournament_selection(pop, fitnesses, k=TOURNAMENT_K):
    selected = random.sample(list(zip(pop, fitnesses)), k)
    selected.sort(key=lambda x: x[1], reverse=True)
    return selected[0][0]


def crossover(p1, p2):
    child = []
    for g1, g2 in zip(p1, p2):
        child.append(g1 if random.random() < 0.5 else g2)
    return repair_crom(child)


def repair_crom(chrom):
    clusters = clusters_from_crom(chrom)
    new_clusters = []
    for c in clusters:
        if not c:
            continue
        subG = G_global.subgraph(c)

        for comp in nx.connected_components(subG):
            comp = list(comp)
            vels = [G_global.nodes[n]['vel'] for n in comp]
            if max(vels) - min(vels) <= DELTA_V:
                new_clusters.append(comp)
            else:

                for n in comp:
                    new_clusters.append([n])
    return crom_from_clusters(new_clusters)


def mutate(chrom, G):
    if random.random() < MUTATION_RATE:

        clusters = clusters_from_crom(chrom)

        valid = [(i, c) for i, c in enumerate(clusters) if len(c) > 1]
        if not valid:
            return chrom
        cid_from, c_from = random.choice(valid)
        n = random.choice(c_from)
        cid_to = random.choice([i for i in range(len(clusters)) if i != cid_from])
    
        c_from_rest = [x for x in c_from if x != n]
        if c_from_rest and not nx.is_connected(G.subgraph(c_from_rest)):
            return chrom
        c_to = clusters[cid_to]
        if not all(abs(G.nodes[n]['vel'] - G.nodes[v]['vel']) <= DELTA_V for v in c_to):
            return chrom
       
        chrom[n] = cid_to
    return chrom


def run_ga(G, pop_size, max_gen):
    global G_global
    G_global = G
    pop = gerar_populacao_inicial(G, pop_size)
    fitnesses = [fitness(c, G) for c in pop]
    best_idx = int(np.argmax(fitnesses))
    best_chrom = pop[best_idx][:]
    best_fit = fitnesses[best_idx]
    no_improve = 0

    for gen in range(1, max_gen + 1):
        new_pop = []
      
        sorted_pop = [c for _, c in sorted(zip(fitnesses, pop), key=lambda x: x[0], reverse=True)]
        new_pop.extend(sorted_pop[:ELITISM_COUNT])
       
        while len(new_pop) < pop_size:
            p1 = tournament_selection(pop, fitnesses)
            p2 = tournament_selection(pop, fitnesses)
            child = crossover(p1, p2)
            child = mutate(child, G)
            new_pop.append(child)
        pop = new_pop
        fitnesses = [fitness(c, G) for c in pop]
        current_best_idx = int(np.argmax(fitnesses))
        current_best_fit = fitnesses[current_best_idx]
        if current_best_fit > best_fit:
            best_fit = current_best_fit
            best_chrom = pop[current_best_idx][:]
            no_improve = 0
        else:
            no_improve += 1
        print(f"[Gen {gen}] Best Fitness = {best_fit:.2f}")
        if no_improve >= 50:
            break
   
    best_clusters = clusters_from_crom(best_chrom)
    outdir = salvar_resultados(G, best_clusters, best_fit)
    return best_clusters, best_fit, outdir


def salvar_resultados(G, clusters, fit):
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUTPUT_DIR, f"GA_{ts}")
    os.makedirs(out, exist_ok=True)
    
    labels = np.full(len(G.nodes), -1)
    for cid, c in enumerate(clusters):
        for n in c:
            labels[n] = cid
    np.save(os.path.join(out, "labels.npy"), labels)
    pickle.dump(clusters, open(os.path.join(out, "clusters.pkl"), "wb"))
    with open(os.path.join(out, "ga_resumo.txt"), "w") as f:
        f.write(f"Fitness: {fit:.2f}\nClusters: {len(clusters)}\n")
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", choices=list(NUM_ROBOS.keys()), required=True)
    parser.add_argument("--pop_size", type=int, default=POP_SIZE)
    parser.add_argument("--max_gen", type=int, default=MAX_GEN)
    args = parser.parse_args()

    
    G = nx.read_graphml(os.path.join(ROOT, f"data/grafo/epsilon_50.0_{NUM_ROBOS[args.instancia]}_seed{SEED}", "grafo.graphml")) if args.tipo == 'sintetico' else nx.read_graphml(os.path.join(ROOT, "data/grafo/roadnet_ca/grafo.graphml"))
    for n in G.nodes:
        for attr in ['x','y','vel','theta','bat']:
            G.nodes[n][attr] = float(G.nodes[n][attr])

    start = time.time()
    best_clusters, best_fit, outdir = run_ga(G, args.pop_size, args.max_gen)
    elapsed = time.time() - start
    print(f"\nGA Final: Fitness = {best_fit:.2f} | Tempo = {elapsed:.2f}s | Saída = {outdir}")

if __name__ == '__main__':
    main()
