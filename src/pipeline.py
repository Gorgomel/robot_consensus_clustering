#!/usr/bin/env python3
import os
import sys
import click

# ------------------------------------------------------------------------------
# Garante que a pasta `src/` (com os pacotes generate/ e graph/) esteja no path
# ------------------------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

@click.group()
def cli():
    """Pipeline do projeto: geração, grafo, clusterização e avaliação."""
    pass

@cli.command(name="generate")
@click.option("--num-robos", type=int, required=True, help="Número de robôs a gerar")
@click.option("--lado", type=int, required=True, help="Tamanho do mapa (lado)")
@click.option("--seed", type=int, default=42, show_default=True, help="Semente para reprodutibilidade")
def generate_command(num_robos, lado, seed):
    """Gera dados sintéticos de robôs."""
    from generate.gerar_dados import gerar_dados_robos
    gerar_dados_robos(seed=seed, tamanho=num_robos, lado=lado)

@cli.command(name="build-graph")
@click.option("--num-robos", type=int, required=True, help="Número de robôs (para localizar a pasta)")
@click.option("--seed", type=int, default=42, show_default=True, help="Semente para reprodutibilidade")
@click.option("--raio", type=float, required=True, help="Raio ε para grafo de visibilidade")
def build_graph_command(num_robos, seed, raio):
    """Constrói grafo ε-ball de visibilidade entre robôs."""
    from graph.construir_grafo import construir_grafo_epsilon_ball
    construir_grafo_epsilon_ball(num_robos=num_robos, seed=seed, raio=raio)

@cli.command(name="cluster")
@click.option("--method", type=click.Choice(['guloso_fo1', 'local_search', 'meta']),
              required=True, help="Heurística a executar")
@click.option("--num-robos", type=int, required=True, help="Número de robôs (para localizar a pasta)")
@click.option("--seed", type=int, default=42, show_default=True, help="Semente para reprodutibilidade")
def cluster_command(method, num_robos, seed):
    """Executa o algoritmo de clusterização escolhido."""
    print(f"[pipeline] Rodando {method}, n={num_robos}, seed={seed}")
    # TODO: importar e disparar a heurística certa de src/heuristics/

@cli.command(name="evaluate")
def evaluate_command():
    """Avalia as soluções geradas (ainda não implementado)."""
    print("[pipeline] Evaluate: pendente de implementação")

if __name__ == "__main__":
    cli()
