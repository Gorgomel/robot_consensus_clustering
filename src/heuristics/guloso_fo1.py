#!/usr/bin/env python3
import os
import sys
import time
import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from config import DELTA_V, SEED, NUM_ROBOS
from tools.io_utils import gerar_nome_pasta

def carregar_grafo_sintetico(instancia):
    pasta_cluster = os.path.join(ROOT_DIR, 'data', 'cluster', f'guloso_{instancia}')
    robos_path = os.path.join(ROOT_DIR, 'data', 'sinteticos', f"robos_{NUM_ROBOS[instancia]}_seed{SEED}", 'robos.npy')
    edges_path = os.path.join(pasta_cluster, 'edges.csv')

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
    pasta_saida = os.path.join(ROOT_DIR, 'data', 'cluster', f'guloso_{instancia}')
    return G, pasta_saida

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
    pasta_saida = os.path.join(ROOT_DIR, 'data', 'grafo', 'roadnet_ca', 'guloso_fo1')
    return G, pasta_saida

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
    return sum(min(G.nodes[n]['vel'] for n in c) for c in clusters if c)

def salvar_resultados(G, clusters, fo1, tempo_exec, pasta_saida):
    os.makedirs(pasta_saida, exist_ok=True)
    resumo = os.path.join(pasta_saida, 'guloso_resumo.txt')
    with open(resumo, 'w') as f:
        f.write(f"Número de clusters: {len(clusters)}\n")
        f.write(f"FO1 = {fo1:.2f}\n")
        f.write(f"Tempo (s) = {tempo_exec:.2f}\n")
    print(f"[OK] Resumo salvo em {resumo}")

    sizes = [len(c) for c in clusters]
    fig, ax = plt.subplots()
    ax.hist(sizes, bins=30, color='purple', edgecolor='black')
    ax.set_xlabel('Tamanho do cluster')
    ax.set_ylabel('Freq.')
    ax.set_title('Distribuição de Tamanhos de Cluster')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'hist_tamanhos.png'))
    plt.close()
    print(f"[OK] Histograma de tamanhos salvo")

def main():
    parser = argparse.ArgumentParser(description='Heurística Gulosa FO1')
    parser.add_argument('--tipo', choices=['sintetico', 'real'], required=True,
                        help='Tipo de instância: sintetico ou real')
    parser.add_argument('--instancia', choices=list(NUM_ROBOS.keys()), default='small',
                        help='Nome da instância sintética (small, medium, large)')
    args = parser.parse_args()

    if args.tipo == 'sintetico':
        G, pasta = carregar_grafo_sintetico(args.instancia)
    else:
        G, pasta = carregar_grafo_real()

    t0 = time.time()
    clusters = guloso_clusterizacao(G)
    tempo_exec = time.time() - t0
    fo1 = calcular_fo1(G, clusters)

    salvar_resultados(G, clusters, fo1, tempo_exec, pasta)

if __name__ == '__main__':
    main()