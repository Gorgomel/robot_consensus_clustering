#!/usr/bin/env python3
import os, sys, click

# add src/ to path
ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

@click.group()
def cli():
    pass

@cli.command()
@click.option("--num-robos", required=True, type=int)
@click.option("--lado", required=True, type=int)
@click.option("--seed", default=42, type=int)
def generate(num_robos, lado, seed):
    from generate.gerar_dados import gerar_dados_robos
    gerar_dados_robos(seed=seed, tamanho=num_robos, lado=lado)

@cli.command()
@click.option("--num-robos", required=True, type=int)
@click.option("--seed", default=42, type=int)
@click.option("--raio", required=True, type=float)
def build_graph(num_robos, seed, raio):
    from graph.construir_grafo import construir_grafo_epsilon_ball
    construir_grafo_epsilon_ball(num_robos=num_robos, seed=seed, raio=raio)

@cli.command()
@click.option("--method", type=click.Choice(["guloso_fo1","local_search","meta"]), required=True)
@click.option("--num-robos", type=int, required=True)
@click.option("--seed", default=42, type=int)
@click.option("--raio", default=50, type=float)
def cluster(method, num_robos, seed, raio):
    if method == "guloso_fo1":
        from heuristics.guloso_fo1 import executar_guloso_fo1
        executar_guloso_fo1(num_robos=num_robos, seed=seed, raio=raio)
    elif method == "local_search":
        from heuristics.local_search import executar_local_search
        executar_local_search(num_robos=num_robos, seed=seed, raio=raio)
    else:
        from heuristics.metaheuristica import executar_meta
        executar_meta(num_robos=num_robos, seed=seed, raio=raio)

@cli.command()
def evaluate():
    # parse all data/cluster/* folders and print a table
    import glob, os
    rows = []
    for method in os.listdir("data/cluster"):
        for inst in os.listdir(f"data/cluster/{method}"):
            resumo = os.path.join("data","cluster",method,inst,"resumo.txt")
            # open resumo, extract lines, append to rows...
    # print markdown or CSV
    pass

@cli.command(name="evaluate")
def evaluate_command():
    """Avalia as soluções geradas e imprime um comparativo em Markdown."""
    import os, re

    header = "| Método              | Instância              | #Clusters | FO₁        | Tempo (s) |"
    print(header)
    print("|---------------------|------------------------|-----------|------------|-----------|")

    cluster_root = "data/cluster"
    for method in sorted(os.listdir(cluster_root)):
        method_dir = os.path.join(cluster_root, method)
        if not os.path.isdir(method_dir):
            continue

        # Casos com arquivos diretos (sem subpastas por instância)
        resumo_path = os.path.join(method_dir, "guloso_resumo.txt")
        if os.path.isfile(resumo_path):
            with open(resumo_path, "r", encoding="utf-8") as f:
                text = f.read()
            method_label = method
            inst_label = "robos_10000_seed42"
        else:
            continue

        m_clusters = re.search(r"Total de clusters:\s*(\d+)", text)
        m_fo1      = re.search(r"FO₁.*?:\s*([\d\.]+)", text)
        m_time     = re.search(r"Tempo de execução:\s*([\d\.]+)", text)

        n_clusters = m_clusters.group(1) if m_clusters else "-"
        fo1_val    = m_fo1.group(1)      if m_fo1      else "-"
        t_exec     = m_time.group(1)     if m_time     else "-"

        print(f"| {method_label:<20} | {inst_label:<22} | {n_clusters:>9} | {fo1_val:>10} | {t_exec:>9} |")


if __name__ == "__main__":
    cli()
