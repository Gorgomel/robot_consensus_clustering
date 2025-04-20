import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.colors import Normalize
from matplotlib import cm

def construir_grafo_epsilon_ball(num_robos, seed, raio, raio_max=200, passo=1.1):
    """
    Constrói um grafo de visibilidade ε-ball com ajuste automático de raio.
    - num_robos: número de robôs (para montar paths)
    - seed: seed usada na geração dos robôs
    - raio: valor inicial de ε
    - raio_max: valor máximo que ε pode alcançar
    - passo: fator de multiplicação de ε a cada iteração (ex: 1.1 = +10%)
    """
    # 1) Paths
    pasta_base = f"data/sinteticos/robos_{num_robos}_seed{seed}"
    grafo_dir  = f"data/grafo/epsilon_{raio:.1f}_{num_robos}_seed{seed}"
    os.makedirs(grafo_dir, exist_ok=True)

    # 2) Carrega estados
    estados = np.load(os.path.join(pasta_base, "robos.npy"))
    posicoes = estados[:, :2]
    velocidades = estados[:, 2]  # coluna de velocidade

    # 3) Ajusta raio até conectar (ou atingir raio_max)
    tree = KDTree(posicoes)
    atual = raio
    while True:
        pares = tree.query_pairs(r=atual)
        G = nx.Graph()
        G.add_nodes_from(range(num_robos))
        # atributos de nó
        for i in range(num_robos):
            x, y, v, theta, bat = estados[i]
            G.nodes[i].update(x=x, y=y, vel=v, theta=theta, bat=bat)
        # arestas
        for i, j in pares:
            d = np.linalg.norm(posicoes[i] - posicoes[j])
            G.add_edge(i, j, weight=d)

        comps = nx.number_connected_components(G)
        if comps == 1 or atual >= raio_max:
            break
        atual *= passo  # aumenta raio em 10%

    # 4) Salva grafo e arestas
    nx.write_graphml(G, os.path.join(grafo_dir, "grafo.graphml"))
    with open(os.path.join(grafo_dir, "edges.csv"), "w") as f:
        f.write("source,target,weight\n")
        for u, v, d in G.edges(data=True):
            f.write(f"{u},{v},{d['weight']:.4f}\n")

    # 5) Estatísticas
    graus = [d for _, d in G.degree()]
    maior_comp = max(len(c) for c in nx.connected_components(G))
    with open(os.path.join(grafo_dir, "stats.txt"), "w") as f:
        f.write(f"n_nodes: {num_robos}\n")
        f.write(f"n_edges: {G.number_of_edges()}\n")
        f.write(f"final_ε: {atual:.4f}\n")
        f.write(f"components: {comps}\n")
        f.write(f"largest_component_size: {maior_comp}\n")
        f.write(f"avg_degree: {np.mean(graus):.4f}\n")
        f.write(f"min_degree: {np.min(graus)}\n")
        f.write(f"max_degree: {np.max(graus)}\n")

    # 6) Desenhos e visualizações
    pos_dict = {i: (estados[i,0], estados[i,1]) for i in range(num_robos)}

    # 6A) Amostra de 1k nós com arestas
    amostra = list(G.nodes)[:1000]
    Gs = G.subgraph(amostra)
    pos_s = {i: pos_dict[i] for i in amostra}
    plt.figure(figsize=(8,6))
    nx.draw(Gs, pos_s, node_size=5, edge_color="gray", width=0.2, alpha=0.4)
    plt.title("Grafo ε-ball (amostra 1k nós)")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grafo_amostra.png"), dpi=300)
    plt.close()

    # 6B) Grafo completo com nós coloridos por velocidade
    norm = Normalize(vmin=np.min(velocidades), vmax=np.max(velocidades))
    cmap = cm.viridis
    node_colors = [cmap(norm(G.nodes[i]["vel"])) for i in G.nodes]

    fig, ax = plt.subplots(figsize=(8,6))
    nx.draw(
        G, pos_dict,
        node_size=5,
        node_color=node_colors,
        edge_color="gray",
        alpha=0.05,
        width=0.01,
        ax=ax
    )
    # agora associamos o colorbar ao próprio axes
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Velocidade")
    plt.title("Grafo ε-ball — nós coloridos por velocidade")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grafo_velocidade.png"), dpi=300)
    plt.close(fig)

    # 6C) Heatmap de densidade de arestas
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

    # 6D) Histograma de grau
    plt.figure(figsize=(6,4))
    plt.hist(graus, bins=30, edgecolor="black")
    plt.xlabel("Grau")
    plt.ylabel("Número de nós")
    plt.title("Histograma de Grau")
    plt.tight_layout()
    plt.savefig(os.path.join(grafo_dir, "grau_hist.png"))
    plt.close()

    print(f"[construir_grafo] grafo e visuais em `{grafo_dir}`")
