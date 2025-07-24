import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering


def carregar_dados(tipo, instancia):
    if tipo == "sintetico":
        caminho = f"data/sinteticos/robos_{instancia}_seed42/robos.npy"
    else:
        caminho = "data/real/robos_roadnet_ca.npy"
    return np.load(caminho)


def salvar_resultados(tipo, instancia, labels, dados):
    pasta = f"data/baselines/aglomerativo_{tipo}_{instancia}"
    os.makedirs(pasta, exist_ok=True)
    np.save(os.path.join(pasta, "labels.npy"), labels)

    # Visualização
    plt.figure(figsize=(6, 6))
    plt.scatter(dados[:, 0], dados[:, 1], c=labels, s=5)
    plt.title("Aglomerativo")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta, "scatter.png"))
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["sintetico", "real"], required=True)
    parser.add_argument("--instancia", required=True)
    args = parser.parse_args()

    dados = carregar_dados(args.tipo, args.instancia)
    clustering = AgglomerativeClustering(n_clusters=5).fit(dados)
    salvar_resultados(args.tipo, args.instancia, clustering.labels_, dados)


if __name__ == "__main__":
    main()
