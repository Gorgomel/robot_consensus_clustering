import os
import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from tools.io_utils import gerar_nome_pasta

def fo1(clusters, G):
    return sum(min(G.nodes[n]["vel"] for n in c) * len(c) for c in clusters)

def clusterizacao_gulosa_fo1(G):
    visitado = set()
    clusters = []

    for no in G.nodes:
        if no in visitado:
            continue
        cluster = set([no])
        fila = [no]
        v_base = G.nodes[no]["vel"]
        while fila:
            atual = fila.pop()
            visitado.add(atual)
            for viz in G.neighbors(atual):
                if viz in visitado:
                    continue
                if abs(G.nodes[viz]["vel"] - v_base) <= 5:
                    cluster.add(viz)
                    fila.append(viz)
                    visitado.add(viz)
        clusters.append(list(cluster))
    return clusters

def carregar_grafo_e_dados(seed, num_robos, raio):
    base_nome = f"robos_{num_robos}_seed{seed}"
    grafo_dir = os.path.join("data", "grafo", f"epsilon_{raio:.1f}_{num_robos}_seed{seed}")
    grafo_path = os.path.join(grafo_dir, "grafo.graphml")
    dados_path = os.path.join("data", "sinteticos", base_nome, "robos.npy")

    if not os.path.exists(grafo_path) or not os.path.exists(dados_path):
        raise FileNotFoundError("Grafo ou dados não encontrados.")

    G = nx.read_graphml(grafo_path)
    dados = np.load(dados_path, allow_pickle=True)
    for i, estado in enumerate(dados):
        G.nodes[str(i)]["x"] = float(estado[0])
        G.nodes[str(i)]["y"] = float(estado[1])
        G.nodes[str(i)]["vel"] = float(estado[2])
        G.nodes[str(i)]["bat"] = float(estado[4])
    return G, dados

def salvar_resultados(clusters, G, tempo_exec, fo1_valor, seed, num_robos, raio):
    pasta = os.path.join("data", "cluster", "guloso_area_maior")
    os.makedirs(pasta, exist_ok=True)

    labels = np.zeros(len(G.nodes), dtype=int)
    for idx, cluster in enumerate(clusters):
        for n in cluster:
            labels[int(n)] = idx
    np.save(os.path.join(pasta, "guloso_labels.npy"), labels)

    # Visualização
    pos = {n: (float(G.nodes[n]["x"]), float(G.nodes[n]["y"])) for n in G.nodes}
    cores = plt.cm.tab20(np.linspace(0, 1, len(clusters)))
    plt.figure(figsize=(10, 8))
    for i, cluster in enumerate(clusters):
        xs = [pos[n][0] for n in cluster]
        ys = [pos[n][1] for n in cluster]
        plt.scatter(xs, ys, s=5, color=cores[i % len(cores)])
    plt.title("Clusterização Gulosa (FO₁)")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta, "guloso_clusters.png"))
    plt.close()

    with open(os.path.join(pasta, "guloso_resumo.txt"), "w") as f:
        f.write(f"Total de clusters: {len(clusters)}\n")
        f.write(f"Valor da função FO₁: {fo1_valor:.2f}\n")
        f.write(f"Tempo de execução: {tempo_exec:.2f} segundos\n")

def executar_guloso_fo1(num_robos, seed, raio=50):
    print("[guloso_fo1] Carregando grafo e dados...")
    G, _ = carregar_grafo_e_dados(seed=seed, num_robos=num_robos, raio=raio)

    print("[guloso_fo1] Executando heurística gulosa (FO₁)...")
    inicio = time.time()
    clusters = clusterizacao_gulosa_fo1(G)
    tempo_exec = time.time() - inicio
    fo1_valor = fo1(clusters, G)

    print(f"[RESULTADO] Clusters: {len(clusters)} | FO₁ = {fo1_valor:.2f} | Tempo = {tempo_exec:.2f}s")
    salvar_resultados(clusters, G, tempo_exec, fo1_valor, seed, num_robos, raio)
    print(f"[guloso_fo1] Resultados salvos com sucesso.")
