#!/usr/bin/env python3
import sys
try:
    import numpy, scipy, matplotlib, networkx, sklearn, pandas, noise, tqdm
except ModuleNotFoundError as e:
    print(f"Dependência faltando: {e.name}. Execute:\n    pip install -r requirements.txt")
    sys.exit(1)

import os
import time
import json
import subprocess
import logging

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# --- SETUP DE LOGGING ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "pipeline.log")
logging.basicConfig(
    filename=LOG_PATH,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# --- CONFIGURAÇÃO GERAL ---
SEED = 42
CHECKPOINT_FILE = os.path.join(LOG_DIR, "pipeline_checkpoint.json")
RESUMO_DIR = "data/resumo"
os.makedirs(RESUMO_DIR, exist_ok=True)

INSTANCIAS = ["small", "medium", "large", "xlarge", "xxlarge"]
TIPOS      = ["sintetico", "real"]
ALGORITMOS = ["guloso", "first", "best", "grasp", "sa", "ils", "ga"]

# Dicionário de templates de comando para cada heurística
COMANDOS_TEMPLATE = {
    "guloso": "python3 src/heuristics/guloso_fo1.py --tipo {tipo} --instancia {instancia}",
    "first":  "python3 src/heuristics/first_improvement_fo1.py --tipo {tipo} --instancia {instancia} --modo first --timeout_iter 180 --max_iter 150",
    "best":   "python3 src/heuristics/best_improvement_fo1.py  --tipo {tipo} --instancia {instancia} --modo best  --timeout_iter 180 --max_iter 150",
    "grasp":  "python3 src/heuristics/grasp_fo1.py           --tipo {tipo} --instancia {instancia}",
    "sa":     "python3 src/heuristics/simulated_annealing_fo1.py --tipo {tipo} --instancia {instancia}",
    "ils":    "python3 src/heuristics/iterated_local_search_fo1.py --tipo {tipo} --instancia {instancia}",
    "ga":     "python3 src/heuristics/genetico_fo1.py   --tipo {tipo} --instancia {instancia}"
}

# Mapeia tamanhos de instância sintética para geração de dados
TAMANHOS_MAP = {"small": 100, "medium": 500, "large": 1000, "xlarge": 5000, "xxlarge": 10000}


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_checkpoint(cp):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(cp, f, indent=2)

def ja_foi_executado(cp, tipo, instancia, etapa):
    return cp.get(tipo, {}).get(instancia, {}).get(etapa, False)

def marcar_como_executado(cp, tipo, instancia, etapa):
    cp.setdefault(tipo, {}).setdefault(instancia, {})[etapa] = True
    save_checkpoint(cp)

def executar_comando(cmd):
    logging.info(f"[EXEC] {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Falha no comando: {cmd}\n{e}")

def carregar_labels(tipo, instancia, algoritmo):
    # Compatível com estrutura de pastas dos scripts
    pasta = f"data/{algoritmo}_results/{tipo}_{instancia}_{algoritmo}"
    caminho = os.path.join(pasta, "labels.npy")
    return np.load(caminho) if os.path.exists(caminho) else None

def carregar_resultado(tipo, instancia, algoritmo):
    pasta = f"data/{algoritmo}_results/{tipo}_{instancia}_{algoritmo}"
    resumo = os.path.join(pasta,
        "refinamento_resumo.txt" if algoritmo in ["first","best","grasp","sa","ils","ga"]
        else f"{algoritmo}_resumo.txt"
    )
    if not os.path.exists(resumo):
        return None
    with open(resumo, 'r') as f:
        linhas = [l.strip() for l in f]
        clusters = int(linhas[0].split(':')[-1])
        fo1      = float(linhas[1].split(':')[-1])
        tempo    = float(linhas[2].split(':')[-1].split()[0])
    return clusters, fo1, tempo

def salvar_tabela(tipo, instancia, resultados):
    df = pd.DataFrame(resultados)
    if df.empty:
        logging.warning(f"Nenhum resultado para {tipo}/{instancia}")
        return
    path_csv = os.path.join(RESUMO_DIR, f"{tipo}_{instancia}_tabela.csv")
    df.to_csv(path_csv, index=False)
    logging.info(f"[TABELA] Salva em {path_csv}")
    gerar_graficos(tipo, instancia, df)

def gerar_graficos(tipo, instancia, df):
    base = os.path.join(RESUMO_DIR, f"{tipo}_{instancia}")
    # FO1, tempo, clusters
    for col, ylabel, sufixo in [
        ("fo1",      "FO₁ final",          "grafico_fo1"),
        ("tempo",    "Tempo (s)",          "grafico_tempo"),
        ("clusters", "Nº de Clusters",     "grafico_clusters")
    ]:
        plt.figure()
        plt.bar(df["algoritmo"], df[col])
        plt.ylabel(ylabel)
        plt.title(f"{ylabel} por algoritmo ({tipo}, {instancia})")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{base}_{sufixo}.png")
        plt.close()
    # ARI / NMI
    if "ari" in df and df["ari"].notna().any():
        plt.figure()
        plt.bar(df["algoritmo"], df["ari"], color="orange")
        plt.ylabel("ARI")
        plt.title(f"ARI vs Guloso ({tipo}, {instancia})")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{base}_grafico_ari.png")
        plt.close()
    if "nmi" in df and df["nmi"].notna().any():
        plt.figure()
        plt.bar(df["algoritmo"], df["nmi"], color="green")
        plt.ylabel("NMI")
        plt.title(f"NMI vs Guloso ({tipo}, {instancia})")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{base}_grafico_nmi.png")
        plt.close()

def pipeline():
    checkpoint = load_checkpoint()

    for tipo in tqdm(TIPOS, desc="Tipos"):
        for instancia in tqdm(INSTANCIAS, desc=f"{tipo}", leave=False):
            logging.info(f"Iniciando {tipo}/{instancia}")

            # 1) Geração de dados sintéticos
            if tipo == "sintetico" and not ja_foi_executado(checkpoint, tipo, instancia, "gerar_dados"):
                tamanho = TAMANHOS_MAP.get(instancia, 1000)
                cmd = f"python3 src/generate/gerar_dados.py --seed {SEED} --tamanho {tamanho}"
                executar_comando(cmd)
                marcar_como_executado(checkpoint, tipo, instancia, "gerar_dados")

            # 2) Construção do grafo
            if not ja_foi_executado(checkpoint, tipo, instancia, "construir_grafo"):
                if tipo == "real":
                    cmd = f"python3 src/graph/construir_grafo.py --tipo {tipo} --instancia {instancia}"
                else:
                    cmd = f"python3 src/graph/construir_grafo.py --instancia {instancia}"
                executar_comando(cmd)
                marcar_como_executado(checkpoint, tipo, instancia, "construir_grafo")

            # 3) Execução das heurísticas
            resultados = []
            labels_ref = carregar_labels(tipo, instancia, "guloso")

            for alg in ALGORITMOS:
                if not ja_foi_executado(checkpoint, tipo, instancia, alg):
                    template = COMANDOS_TEMPLATE.get(alg)
                    if not template:
                        logging.warning(f"Sem template para {alg}")
                        continue
                    cmd = template.format(tipo=tipo, instancia=instancia)
                    executar_comando(cmd)
                    marcar_como_executado(checkpoint, tipo, instancia, alg)

                res = carregar_resultado(tipo, instancia, alg)
                labels = carregar_labels(tipo, instancia, alg)
                if res and labels_ref is not None and labels is not None:
                    clusters, fo1, tempo = res
                    try:
                        ari = adjusted_rand_score(labels_ref, labels)
                        nmi = normalized_mutual_info_score(labels_ref, labels)
                    except Exception:
                        ari = nmi = None
                    resultados.append({
                        "algoritmo": alg,
                        "clusters": clusters,
                        "fo1": fo1,
                        "tempo": tempo,
                        "ari": ari,
                        "nmi": nmi
                    })

            salvar_tabela(tipo, instancia, resultados)
            logging.info(f"Concluído {tipo}/{instancia}\n")
            time.sleep(1)

if __name__ == "__main__":
    pipeline()
