# src/heuristicas/clusterizar_guloso_fo1.py
import numpy as np
import networkx as nx
import time, os, argparse
from config import RAIO_COMUNICACAO
from scipy.spatial import cKDTree
from plots import plot_scatter

def carregar_grafo(base_dir):
    path = os.path.join(base_dir,'data','grafo','grafo_epsilon.graphml')
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    G = nx.read_graphml(path)
    return G

def greedy_cluster_fo1(G, tol_vel=5.0):
    visit, clusters = set(), []
    for u in G.nodes():
        if u in visit: continue
        visit.add(u)
        c = {u}
        queue=[u]
        v0 = float(G.nodes[u].get('vel',0))
        while queue:
            x = queue.pop()
            for w in G[x]:
                if w in visit: continue
                v_w = float(G.nodes[w].get('vel',0))
                if abs(v0-v_w)<=tol_vel:
                    c.add(w); visit.add(w); queue.append(w)
        clusters.append(list(c))
    return clusters

def fo1(clusters,G):
    total=0
    for C in clusters:
        vs=[float(G.nodes[n]['vel']) for n in C]
        total+= min(vs)*len(C)
    return total

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--tol', type=float, default=5.0)
    args=p.parse_args()

    base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
    print("[guloso] carregando grafo…")
    G = carregar_grafo(base)

    # injete velocidades no grafo, se ausentes
    robos = np.load(os.path.join(base,'data','sinteticos','robos.npy'))
    for i,row in enumerate(robos):
        if 'vel' not in G.nodes[str(i)]:
            G.nodes[str(i)]['vel']= float(row[2])

    print("[guloso] executando clusterização…")
    t0=time.time()
    clusters=greedy_cluster_fo1(G, args.tol)
    dt=time.time()-t0

    score=fo1(clusters,G)
    print(f"[RESULTADO] C={len(clusters)}  FO1={score:.2f}  tempo={dt:.3f}s")

    # saída
    outdir=os.path.join(base,'data','cluster','guloso')
    os.makedirs(outdir,exist_ok=True)

    # plot
    xs=[float(G.nodes[n]['x']) for n in G.nodes()]
    ys=[float(G.nodes[n]['y']) for n in G.nodes()]
    # cor por cluster
    label = np.zeros(G.number_of_nodes(),dtype=int)
    for idx,C in enumerate(clusters):
        for u in C: label[int(u)] = idx
    plot_scatter(xs,ys,c=label, cmap='tab20',
                 title="Guloso FO1",xlabel="X",ylabel="Y",
                 out_path=os.path.join(outdir,'clusters.png'))

    # salvar rótulos e resumo
    np.save(os.path.join(outdir,'labels.npy'), label)
    with open(os.path.join(outdir,'resumo.txt'),'w') as f:
        f.write(f"Clusters: {len(clusters)}\n")
        f.write(f"FO1: {score:.2f}\n")
        f.write(f"Tempo: {dt:.3f}s\n")
        sizes=sorted([len(C) for C in clusters], reverse=True)
        f.write("Maiores clusters: "+",".join(map(str,sizes[:5]))+"\n")

    print(f"[guloso] resultados em {outdir}")
