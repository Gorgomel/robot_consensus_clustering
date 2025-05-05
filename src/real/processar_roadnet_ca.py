import os
import gzip
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.colors import Normalize
from matplotlib import cm

def carregar_roadnet_arquivo(caminho):
    G = nx.Graph()
    with gzip.open(caminho, 'rt') as f:
        for linha in f:
            if linha.startswith('#'):
                continue
            u, v = map(int, linha.strip().split())
            G.add_edge(u, v)
    return G

def amostrar_subgrafo(G, num_nos=10000, seed=42):
    print(f"[INFO] Amostrando {num_nos} nós conectados...")
    np.random.seed(seed)
    nos_amostrados = set()
    fila = [np.random.choice(list(G.nodes))]
    while len(nos_amostrados) < num_nos and fila:
        atual = fila.pop()
        if atual not in nos_amostrados:
            nos_amostrados.add(atual)
            fila.extend(G.neighbors(atual))
    subG = G.subgraph(nos_amostrados).copy()
    print(f"[OK] Subgrafo com {subG.number_of_nodes()} nós e {subG.number_of_edges()} arestas")
    return subG

def atribuir_atributos(G, seed=42):
    np.random.seed(seed)
    print("[INFO] Atribuindo atributos aos nós...")

    pos = nx.spring_layout(G, seed=seed, k=0.15)

    for n in G.nodes:
        grau = G.degree[n]
        G.nodes[n]['x'], G.nodes[n]['y'] = pos[n]
        G.nodes[n]['vel'] = np.log(grau + 1) * 10
        G.nodes[n]['theta'] = np.random.uniform(0, 2*np.pi)
        G.nodes[n]['bat'] = np.random.uniform(20, 100)

    return G

def salvar_grafo(G, pasta_saida):
    os.makedirs(pasta_saida, exist_ok=True)

    # Salvar como .graphml
    nx.write_graphml(G, os.path.join(pasta_saida, "grafo.graphml"))

    # Salvar CSV de arestas com pesos (distância euclidiana)
    with open(os.path.join(pasta_saida, "edges.csv"), "w") as f:
        f.write("source,target,weight\n")
        for u, v in G.edges():
            d = np.linalg.norm([
                G.nodes[u]['x'] - G.nodes[v]['x'],
                G.nodes[u]['y'] - G.nodes[v]['y']
            ])
            f.write(f"{u},{v},{d:.4f}\n")

    # Estatísticas
    graus = [G.degree[n] for n in G.nodes]
    with open(os.path.join(pasta_saida, "stats.txt"), "w") as f:
        f.write(f"n_nodes: {G.number_of_nodes()}\n")
        f.write(f"n_edges: {G.number_of_edges()}\n")
        f.write(f"avg_degree: {np.mean(graus):.2f}\n")
        f.write(f"min_degree: {np.min(graus)}\n")
        f.write(f"max_degree: {np.max(graus)}\n")
        f.write(f"Data: {datetime.now()}\n")

    # Visualização por velocidade
    norm = Normalize(vmin=min(nx.get_node_attributes(G, "vel").values()),
                     vmax=max(nx.get_node_attributes(G, "vel").values()))
    cmap = cm.viridis
    node_colors = [cmap(norm(G.nodes[n]["vel"])) for n in G.nodes]
    pos_plot = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes}

    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(G, pos_plot, node_color=node_colors, node_size=5, edge_color="gray", alpha=0.3, width=0.1, ax=ax)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Velocidade (log(grau+1) × 10)")
    ax.set_title("RoadNet-CA (subgrafo) com velocidade estimada")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafo_velocidade.png"), dpi=300)
    plt.close()

    print(f"[OK] Grafo salvo em {pasta_saida}")

def main():
    nome_arquivo = "roadNet-CA.txt.gz"
    caminho_dados = os.path.join("data", "externo")
    caminho_arquivo = os.path.join(caminho_dados, nome_arquivo)
    pasta_saida = os.path.join("data", "grafo", "roadnet_ca")

    os.makedirs(caminho_dados, exist_ok=True)

    if not os.path.exists(caminho_arquivo):
        print(f"[ERRO] Arquivo não encontrado: {caminho_arquivo}")
        print("Baixe manualmente de: https://snap.stanford.edu/data/roadNet-CA.html")
        return

    print("[INFO] Carregando grafo completo...")
    G = carregar_roadnet_arquivo(caminho_arquivo)
    print(f"[INFO] Grafo original: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas")

    G = amostrar_subgrafo(G, num_nos=10000, seed=42)
    G = atribuir_atributos(G, seed=42)
    salvar_grafo(G, pasta_saida)

if __name__ == "__main__":
    main()
