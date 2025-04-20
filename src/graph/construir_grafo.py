# src/construir_grafo.py
import numpy as np
import networkx as nx
import os
import argparse
from scipy.spatial import cKDTree
from plots import plot_scatter, plot_histogram

def construir_grafo(posicoes, raio):
    tree = cKDTree(posicoes)
    nbrs = tree.query_ball_point(posicoes, r=raio)
    G = nx.Graph()
    for i,(x,y) in enumerate(posicoes):
        G.add_node(i, x=float(x), y=float(y))
    for i, vs in enumerate(nbrs):
        for j in vs:
            if i<j:
                dist = np.linalg.norm(posicoes[i]-posicoes[j])
                G.add_edge(i,j, peso=float(dist))
    return G

def exportar(G, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    gml = os.path.join(out_dir,'grafo_epsilon.graphml')
    nx.write_graphml(G, gml)
    print(f"[grafo] GraphML: {gml}")

    edf = [(u,v,d['peso']) for u,v,d in G.edges(data=True)]
    import pandas as pd
    pd.DataFrame(edf,columns=['u','v','peso']) \
      .to_csv(os.path.join(out_dir,'grafo_epsilon_arestas.csv'),index=False)
    print(f"[grafo] CSV: {out_dir}/grafo_epsilon_arestas.csv")

    # hist de grau
    graus = np.array([d for _,d in G.degree()])
    plot_histogram(graus, bins=50, title="Histograma de Grau",xlabel="Grau",ylabel="Freq",
                   out_path=os.path.join(out_dir,'grafo_epsilon_hist_grau.png'))

    # hist de peso
    pesos = np.array([d['peso'] for _,_,d in G.edges(data=True)])
    plot_histogram(pesos, bins=50, title="Histograma de pesos das arestas",
                   xlabel="distância", ylabel="freq",
                   out_path=os.path.join(out_dir,'grafo_epsilon_hist_peso.png'))

    # scatter
    xs = np.array([G.nodes[n]['x'] for n in G.nodes()])
    ys = np.array([G.nodes[n]['y'] for n in G.nodes()])
    plot_scatter(xs,ys, title="Grafo ε‑ball", xlabel="X", ylabel="Y",
                 out_path=os.path.join(out_dir,'grafo_epsilon.png'))

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--raio', type=float, default=10.0)
    args = p.parse_args()

    base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    robos = np.load(os.path.join(base,'data','sinteticos','robos.npy'))
    pos = robos[:,0:2]
    G = construir_grafo(pos, args.raio)
    exportar(G, os.path.join(base,'data','grafo'))
