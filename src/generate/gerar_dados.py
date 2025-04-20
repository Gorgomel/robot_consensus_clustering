# src/gerar_dados.py
import numpy as np
import os
import argparse
from noise import pnoise2
from config import NUM_ROBOS, MODO_GERACAO, SEED, TAMANHO_CIDADE
from plots import plot_heatmap, plot_histogram, plot_scatter

def gerar_densidade_perlin(lado, escala, octaves, seed):
    dens = np.zeros((lado, lado), dtype=float)
    for i in range(lado):
        for j in range(lado):
            dens[i,j] = pnoise2(i/escala, j/escala, octaves=octaves,
                                repeatx=lado, repeaty=lado, base=seed)
    dens -= dens.min()
    dens /= dens.max()
    return dens

def amostrar_por_densidade(dens, n, seed):
    np.random.seed(seed)
    idx = np.random.choice(dens.size, size=n, replace=False, p=dens.ravel()/dens.sum())
    coords = np.vstack(np.unravel_index(idx, dens.shape)).T
    jitter = np.random.uniform(0,1,(n,2))
    return (coords + jitter)

def gerar_dados(n, modo, seed, tamanho):
    np.random.seed(seed)
    if modo == 'densidade_realista':
        dens = gerar_densidade_perlin(lado=tamanho, escala=20, octaves=4, seed=seed)
        pos = amostrar_por_densidade(dens, n, seed)
        x, y = pos[:,0:1], pos[:,1:2]
    elif modo == 'uniforme':
        x = np.random.uniform(0,tamanho,(n,1))
        y = np.random.uniform(0,tamanho,(n,1))
    elif modo == 'grade':
        lado = int(np.ceil(np.sqrt(n)))
        gx, gy = np.meshgrid(np.linspace(0,tamanho,lado), np.linspace(0,tamanho,lado))
        pos = np.vstack([gx.ravel(), gy.ravel()]).T[:n]
        pos += np.random.uniform(-2,2,pos.shape)
        x,y = pos[:,0:1], pos[:,1:2]
    else:
        raise ValueError(f"Modo '{modo}' não reconhecido")

    v = np.random.normal(30,5,(n,1))
    v = np.clip(v, 0, 100)  # validação
    theta = np.random.uniform(0,2*np.pi,(n,1))
    b = np.random.uniform(20,100,(n,1))

    estados = np.hstack((x,y,v,theta,b))
    # salve
    base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    out = os.path.join(base,'data','sinteticos','robos.npy')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    np.save(out, estados)
    print(f"[gerar_dados] {n} robôs salvos em {out}")

    # visualizações
    plot_heatmap(dens if modo=='densidade_realista' else np.zeros((1,1)),
                 "Mapa de densidade (Perlin)", "X","Y","densidade",
                 out.replace('robos.npy','heatmap_densidade.png'))
    plot_histogram(b.ravel(), bins=30, title="Distribuição de Bateria",
                   xlabel="Bateria (%)", ylabel="Freq",
                   out_path=out.replace('robos.npy','hist_bateria.png'))
    plot_histogram(v.ravel(), bins=30, title="Distribuição de Velocidade",
                   xlabel="Velocidade", ylabel="Freq",
                   out_path=out.replace('robos.npy','hist_velocidade.png'))
    plot_scatter(x.ravel(), y.ravel(), c=v.ravel(),
                 title="Posições x Velocidade", xlabel="X", ylabel="Y",
                 out_path=out.replace('robos.npy','posicoes_velocidade.png'))

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=NUM_ROBOS)
    p.add_argument('--modo', type=str, default=MODO_GERACAO)
    p.add_argument('--seed', type=int, default=SEED)
    p.add_argument('--size', type=int, default=TAMANHO_CIDADE)
    args = p.parse_args()
    gerar_dados(args.n, args.modo, args.seed, args.size)
