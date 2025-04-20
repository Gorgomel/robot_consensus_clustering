#!/usr/bin/env python3
import numpy as np
import os
from datetime import datetime
from pathlib import Path
from tools.io_utils import gerar_nome_pasta
from noise import pnoise2
import matplotlib.pyplot as plt

def gerar_densidade_perlin(tamanho, escala, octaves, seed):
    np.random.seed(seed)
    dens = np.zeros((tamanho, tamanho))
    for i in range(tamanho):
        for j in range(tamanho):
            dens[i, j] = pnoise2(i / escala, j / escala,
                                 octaves=octaves, repeatx=tamanho,
                                 repeaty=tamanho, base=seed)
    dens -= dens.min()
    dens /= dens.max()
    return dens

def amostrar_por_densidade(densidade, n_amostras, seed=42):
    np.random.seed(seed)
    tamanho = densidade.shape[0]
    coords = np.array([(i, j) for i in range(tamanho) for j in range(tamanho)])
    probs = densidade.flatten()
    probs /= probs.sum()
    idx = np.random.choice(len(coords), size=n_amostras, replace=False, p=probs)
    selecionados = coords[idx] + np.random.uniform(0, 1, size=(n_amostras, 2))
    return selecionados

def gerar_dados_robos(seed, tamanho, lado):
    """
    Gera:
     - dados em data/sinteticos/<nome>/
     - robos.npy, quatro PNGs (scatter, hist velo, hist bat, heatmap densidade)
     - resumo.txt
    """
    np.random.seed(seed)

    # ==== nome e pasta ====
    base_dir = Path("data") / "sinteticos"
    base_dir.mkdir(parents=True, exist_ok=True)
    base_nome = f"robos_{tamanho}"
    pasta_str = gerar_nome_pasta(str(base_dir), base_nome, seed)
    path = Path(pasta_str)

    # ==== gerar densidade e posições ====
    densidade = gerar_densidade_perlin(lado, escala=30, octaves=4, seed=seed)
    posicoes = amostrar_por_densidade(densidade, n_amostras=tamanho, seed=seed)

    # ==== velocidades correlacionadas com densidade ====
    # índice inteiro para lookup
    pos_idx = np.floor(posicoes).astype(int)
    pos_idx[:, 0] = np.clip(pos_idx[:, 0], 0, lado-1)
    pos_idx[:, 1] = np.clip(pos_idx[:, 1], 0, lado-1)
    dens_at_pos = densidade[pos_idx[:, 0], pos_idx[:, 1]]
    mu, beta, sigma = 30, 10, 5
    velocidades = np.clip(
        np.random.normal(loc=mu - beta * dens_at_pos, scale=sigma, size=tamanho),
        10, 50
    )

    # ==== demais atributos ====
    baterias = np.random.uniform(20, 100, size=tamanho)
    direcoes = np.random.uniform(0, 2 * np.pi, size=tamanho)

    estados = np.column_stack((posicoes, velocidades, direcoes, baterias))
    np.save(path / "robos.npy", estados)

    # ==== visualizações ====
    x, y = posicoes[:, 0], posicoes[:, 1]

    # scatter posição vs velocidade
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(x, y, c=velocidades, cmap='viridis', s=10)
    plt.colorbar(sc, label="Velocidade")
    plt.title("Posições coloridas por velocidade")
    plt.xlabel("X"); plt.ylabel("Y")
    plt.tight_layout()
    plt.savefig(path / "posicoes_velocidade.png")
    plt.close()

    # histograma de velocidades
    plt.figure(figsize=(6, 4))
    plt.hist(velocidades, bins=30, edgecolor='black')
    plt.title("Histograma de velocidades")
    plt.xlabel("Velocidade"); plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig(path / "hist_velocidade.png")
    plt.close()

    # histograma de bateria
    plt.figure(figsize=(6, 4))
    plt.hist(baterias, bins=30, edgecolor='black', color='green')
    plt.title("Histograma de bateria")
    plt.xlabel("Bateria"); plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig(path / "hist_bateria.png")
    plt.close()

    # heatmap de densidade
    plt.figure(figsize=(6, 6))
    im = plt.imshow(densidade, origin='lower', cmap='inferno')
    plt.colorbar(im, label="Densidade")
    plt.title("Heatmap da densidade (Perlin)")
    plt.xlabel("X"); plt.ylabel("Y")
    plt.tight_layout()
    plt.savefig(path / "heatmap_densidade.png")
    plt.close()

    # ==== resumo.txt ====
    with open(path / "resumo.txt", "w", encoding="utf-8") as f:
        f.write("Geração de robôs\n")
        f.write(f"Seed: {seed}\n")
        f.write(f"Quantidade: {tamanho}\n")
        f.write(f"Área da cidade: {lado} x {lado}\n")
        f.write(f"Data e hora: {datetime.now()}\n")

    print(f"[generate_data] Dados gerados com sucesso em: {path}")

# Para teste via CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tamanho", type=int, default=10000)
    parser.add_argument("--lado", type=int, default=3000)
    args = parser.parse_args()
    gerar_dados_robos(seed=args.seed, tamanho=args.tamanho, lado=args.lado)
