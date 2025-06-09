import os
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Configuração geral
INSTANCIAS = [100, 500, 1000, 5000, 10000]
TIPOS = ["sintetico", "real"]
ALGORITMOS = ["guloso", "first", "best", "louvain", "kmeans", "spectral", "aglomerativo"]
SEED = 42
CHECKPOINT_FILE = "logs/pipeline_checkpoint.json"
RESUMO_DIR = "data/resumo"

# Criar pastas se não existirem
os.makedirs("logs", exist_ok=True)
os.makedirs(RESUMO_DIR, exist_ok=True)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def ja_foi_executado(checkpoint, tipo, instancia, algoritmo):
    return checkpoint.get(tipo, {}).get(str(instancia), {}).get(algoritmo, False)

def marcar_como_executado(checkpoint, tipo, instancia, algoritmo):
    checkpoint.setdefault(tipo, {}).setdefault(str(instancia), {})[algoritmo] = True
    save_checkpoint(checkpoint)

def executar_comando(comando):
    print(f"\n[EXECUTANDO] {comando}")
    os.system(comando)

def carregar_labels(tipo, instancia, algoritmo):
    if algoritmo in ["first", "best"]:
        pasta = f"data/{algoritmo}_improvement/{tipo}_{instancia}_{algoritmo}"
    elif algoritmo == "guloso":
        pasta = f"data/cluster/{tipo}_{instancia}_guloso_fo1"
    else:
        pasta = f"data/cluster/{tipo}_{instancia}_{algoritmo}"
    caminho = os.path.join(pasta, "labels.npy")
    if os.path.exists(caminho):
        return np.load(caminho)
    return None

def carregar_resultado(tipo, instancia, algoritmo):
    if algoritmo in ["first", "best"]:
        pasta = f"data/{algoritmo}_improvement/{tipo}_{instancia}_{algoritmo}"
        resumo = os.path.join(pasta, "refinamento_resumo.txt")
    elif algoritmo == "guloso":
        pasta = f"data/cluster/{tipo}_{instancia}_guloso_fo1"
        resumo = os.path.join(pasta, "guloso_resumo.txt")
    else:
        pasta = f"data/cluster/{tipo}_{instancia}_{algoritmo}"
        resumo = os.path.join(pasta, f"{algoritmo}_resumo.txt")

    if not os.path.exists(resumo):
        return None

    with open(resumo, 'r') as f:
        linhas = f.readlines()
        clusters = int(linhas[0].split(':')[-1].strip())
        fo1 = float(linhas[1].split(':')[-1].strip())
        tempo = float(linhas[2].split(':')[-1].split()[0])
        return clusters, fo1, tempo

def salvar_tabela(tipo, instancia, resultados):
    df = pd.DataFrame(resultados)
    caminho = f"{RESUMO_DIR}/{tipo}_{instancia}_tabela.csv"
    df.to_csv(caminho, index=False)
    print(f"[TABELA] Resultados salvos em {caminho}")
    gerar_graficos(tipo, instancia, df)

def gerar_graficos(tipo, instancia, df):
    base = f"{RESUMO_DIR}/{tipo}_{instancia}"

    # FO1
    plt.figure()
    plt.bar(df["algoritmo"], df["fo1"])
    plt.ylabel("FO₁ final")
    plt.title(f"FO₁ por algoritmo ({tipo}, {instancia} robôs)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{base}_grafico_fo1.png")
    plt.close()

    # Tempo
    plt.figure()
    plt.bar(df["algoritmo"], df["tempo"])
    plt.ylabel("Tempo (s)")
    plt.title(f"Tempo de execução por algoritmo ({tipo}, {instancia} robôs)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{base}_grafico_tempo.png")
    plt.close()

    # Clusters
    plt.figure()
    plt.bar(df["algoritmo"], df["clusters"])
    plt.ylabel("Nº de Clusters")
    plt.title(f"Clusters gerados por algoritmo ({tipo}, {instancia} robôs)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{base}_grafico_clusters.png")
    plt.close()

    # ARI
    if "ari" in df.columns and df["ari"].notna().any():
        plt.figure()
        plt.bar(df["algoritmo"], df["ari"], color="orange")
        plt.ylabel("ARI (Rand Index)")
        plt.title(f"ARI vs Guloso ({tipo}, {instancia} robôs)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{base}_grafico_ari.png")
        plt.close()

    # NMI
    if "nmi" in df.columns and df["nmi"].notna().any():
        plt.figure()
        plt.bar(df["algoritmo"], df["nmi"], color="green")
        plt.ylabel("NMI")
        plt.title(f"NMI vs Guloso ({tipo}, {instancia} robôs)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{base}_grafico_nmi.png")
        plt.close()

def pipeline():
    checkpoint = load_checkpoint()
    
    for tipo in TIPOS:
        for instancia in INSTANCIAS:
            print("="*60)
            print(f"PROCESSANDO: Tipo = {tipo} | Instância = {instancia}")
            print("="*60)

            # 1. Gera dados sintéticos se for tipo sintético
            if tipo == "sintetico" and not ja_foi_executado(checkpoint, tipo, instancia, "gerar_dados"):
                comando = f"python3 src/generate/gerar_dados.py --seed {SEED} --tamanho {instancia}"
                executar_comando(comando)
                marcar_como_executado(checkpoint, tipo, instancia, "gerar_dados")

            # 2. Constrói grafo
            if not ja_foi_executado(checkpoint, tipo, instancia, "construir_grafo"):
                comando = f"python3 src/graph/construir_grafo.py --instancia {instancia} --tipo {tipo}"
                executar_comando(comando)
                marcar_como_executado(checkpoint, tipo, instancia, "construir_grafo")

            # 3. Executa todos os algoritmos
            for algoritmo in ALGORITMOS:
                if not ja_foi_executado(checkpoint, tipo, instancia, algoritmo):
                    if algoritmo in ["guloso"]:
                        comando = f"python3 src/heuristics/guloso_fo1.py --tipo {tipo} --instancia {instancia}"
                    elif algoritmo == "first":
                        comando = f"python3 src/heuristics/first_improvement_fo1.py --tipo {tipo} --instancia {instancia} --modo first --timeout_iter 180 --max_iter 150"
                    elif algoritmo == "best":
                        comando = f"python3 src/heuristics/best_improvement_fo1.py --tipo {tipo} --instancia {instancia} --modo best --timeout_iter 180 --max_iter 150"
                    else:
                        comando = f"python3 src/cluster_baselines/{algoritmo}.py --tipo {tipo} --instancia {instancia}"

                    executar_comando(comando)
                    marcar_como_executado(checkpoint, tipo, instancia, algoritmo)

            # 4. Coleta resultados e gera tabela + gráficos
            resultados = []
            labels_guloso = carregar_labels(tipo, instancia, "guloso")
            for algoritmo in ALGORITMOS:
                res = carregar_resultado(tipo, instancia, algoritmo)
                labels = carregar_labels(tipo, instancia, algoritmo)
                if res:
                    clusters, fo1, tempo = res
                    ari = nmi = None
                    if labels_guloso is not None and labels is not None:
                        try:
                            ari = adjusted_rand_score(labels_guloso, labels)
                            nmi = normalized_mutual_info_score(labels_guloso, labels)
                        except Exception:
                            pass
                    resultados.append({
                        "algoritmo": algoritmo,
                        "clusters": clusters,
                        "fo1": fo1,
                        "tempo": tempo,
                        "ari": ari,
                        "nmi": nmi
                    })
            salvar_tabela(tipo, instancia, resultados)
            print("\n[OK] Instância finalizada. Passando para a próxima.\n")
            time.sleep(1)

if __name__ == "__main__":
    pipeline()
