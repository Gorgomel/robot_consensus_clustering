#!/usr/bin/env python3
import os
import sys
import time
import argparse
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from config import DELTA_V, SEED, NUM_ROBOS


def print_header(args):
    print("\n" + "=" * 60)
    print(f"  EXECUÇÃO INICIADA")
    print(f"  Modo:     guloso")
    print(f"  Tipo:     {args.tipo}")
    print(f"  Instância:{args.instancia}")
    print("=" * 60 + "\n")


def print_footer(fo1, tempo_total, clusters, pasta_saida):
    print("\n" + "=" * 60)
    print("  EXECUÇÃO FINALIZADA")
    print(f"  Clusters finais: {len(clusters)}")
    print(f"  FO₁ final:        {fo1:.2f}")
    print(f"  Tempo total:      {tempo_total:.4f} segundos")
    print(f"  Resultados em:    {pasta_saida}")
    print("=" * 60 + "\n")


def carregar_grafo_sintetico(instancia):
    pasta_grafo = os.path.join(ROOT_DIR, 'data', 'grafo', f"epsilon_50.0_{NUM_ROBOS[instancia]}_seed{SEED}")
    robos_path = os.path.join(pasta_grafo, 'robos.npy')
    edges_path = os.path.join(pasta_grafo, 'edges.csv')

    if not os.path.exists(robos_path) or not os.path.exists(edges_path):
        raise FileNotFoundError("Arquivos sintéticos não encontrados. Execute gerar_dados.py e construir_grafo.py.")

    G = nx.Graph()
    dados = np.load(robos_path, allow_pickle=True)
    for i, estado in enumerate(dados):
        x, y, vel, theta, bat = estado
        G.add_node(i, x=float(x), y=float(y), vel=float(vel), theta=float(theta), bat=float(bat))
    with open(edges_path) as f:
        next(f)
        for linha in f:
            u, v, _ = linha.strip().split(',')
            G.add_edge(int(u), int(v))
    return G


def carregar_grafo_real():
    graphml_path = os.path.join(ROOT_DIR, 'data', 'grafo', 'roadnet_ca', 'grafo.graphml')
    if not os.path.exists(graphml_path):
        raise FileNotFoundError(f"Grafo real não encontrado em {graphml_path}. Execute processar_roadnet_ca.py primeiro.")
    G = nx.read_graphml(graphml_path)
    for n in G.nodes:
        G.nodes[n]['x']     = float(G.nodes[n]['x'])
        G.nodes[n]['y']     = float(G.nodes[n]['y'])
        G.nodes[n]['vel']   = float(G.nodes[n]['vel'])
        G.nodes[n]['theta'] = float(G.nodes[n]['theta'])
        G.nodes[n]['bat']   = float(G.nodes[n]['bat'])
    return G


def guloso_clusterizacao(G):
    clusters = []
    visitado = set()
    for node in sorted(G.nodes, key=lambda n: -G.nodes[n]['vel']):
        if node in visitado:
            continue
        cluster = [node]
        visitado.add(node)
        for viz in G.neighbors(node):
            if viz not in visitado and abs(G.nodes[node]['vel'] - G.nodes[viz]['vel']) <= DELTA_V:
                cluster.append(viz)
                visitado.add(viz)
        clusters.append(cluster)
    return clusters


def calcular_fo1(G, clusters):
    return sum(min(G.nodes[n]['vel'] for n in c) * len(c) for c in clusters if c)


def salvar_resultados(G, clusters, fo1, tempo_exec, pasta_saida):
    os.makedirs(pasta_saida, exist_ok=True)

    with open(os.path.join(pasta_saida, 'guloso_resumo.txt'), 'w') as f:
        f.write(f"Número de clusters: {len(clusters)}\n")
        f.write(f"FO1 = {fo1:.2f}\n")
        f.write(f"Tempo (s) = {tempo_exec:.4f}\n")

    # Histograma de tamanhos
    sizes = [len(c) for c in clusters]
    fig, ax = plt.subplots()
    ax.hist(sizes, bins=30, color='purple', edgecolor='black')
    ax.set_xlabel('Tamanho do cluster')
    ax.set_ylabel('Freq.')
    ax.set_title('Distribuição de Tamanhos de Cluster')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'hist_tamanhos.png'))
    plt.close()

    # Histograma das velocidades mínimas por cluster
    min_vels = [min(G.nodes[n]['vel'] for n in c) for c in clusters if c]
    plt.figure(figsize=(6, 4))
    plt.hist(min_vels, bins=30, edgecolor="black", color="orange")
    plt.xlabel("Velocidade mínima")
    plt.ylabel("Frequência")
    plt.title("Velocidade mínima por cluster (FO₁)")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'hist_min_velocidade.png'))
    plt.close()

    # Scatter plot
    pos = np.array([[G.nodes[n]['x'], G.nodes[n]['y']] for n in G.nodes])
    labels = np.full(len(G.nodes), -1)
    for cid, cluster in enumerate(clusters):
        for n in cluster:
            labels[int(n)] = cid
    plt.figure(figsize=(7, 6))
    plt.scatter(pos[:, 0], pos[:, 1], c=labels, cmap='tab20', s=5, alpha=0.7)
    plt.title("Clusters - Posição dos vértices")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'scatter_clusters.png'), dpi=300)
    plt.close()

    # Salvar labels e clusters
    np.save(os.path.join(pasta_saida, "labels.npy"), labels)
    with open(os.path.join(pasta_saida, "clusters.pkl"), "wb") as f:
        pickle.dump(clusters, f)


def main():
    parser = argparse.ArgumentParser(description='Heurística Gulosa FO₁')
    parser.add_argument('--tipo', choices=['sintetico', 'real'], required=True,
                        help='Tipo de instância: sintetico ou real')
    parser.add_argument('--instancia', choices=list(NUM_ROBOS.keys()),
                        help='Nome da instância sintética (ex: small, medium, large)')
    parser.add_argument('--output_dir', default=os.path.join(ROOT_DIR, 'data', 'cluster'),
                        help='Diretório base para salvar resultados')
    args = parser.parse_args()

    if args.tipo == 'sintetico' and not args.instancia:
        parser.error("--instancia é obrigatório para tipo sintetico")

    print_header(args)

    if args.tipo == 'sintetico':
        G = carregar_grafo_sintetico(args.instancia)
        pasta = os.path.join(args.output_dir, f'{args.tipo}_{args.instancia}_guloso_fo1')
    else:
        G = carregar_grafo_real()
        pasta = os.path.join(args.output_dir, f'real_guloso_fo1')

    t0 = time.time()
    clusters = guloso_clusterizacao(G)
    tempo_exec = time.time() - t0
    fo1 = calcular_fo1(G, clusters)

    salvar_resultados(G, clusters, fo1, tempo_exec, pasta)
    print_footer(fo1, tempo_exec, clusters, pasta)


if __name__ == '__main__':
    main()
