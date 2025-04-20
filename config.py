# config.py
"""
Configurações globais para o projeto de clusterização de robôs autônomos.

Este arquivo define todos os parâmetros fixos usados por:
 - geração de dados sintéticos
 - construção do grafo ε‑ball
 - heurísticas de clusterização
"""

# =====================================================
# Instâncias e escalas
# =====================================================
# Número de robôs por instância
NUM_ROBOS = {
    'small': 300,     # debug / validação manual
    'medium': 3000,   # comparação entre heurísticas
    'large': 10000,   # avaliação de escalabilidade
}

# Tamanho da área (unidades de coordenadas) correspondente
TAMANHO_AREA = {
    'small': 300,     # 300×300
    'medium': 1000,   # 1000×1000
    'large': 3000,    # 3000×3000
}

# =====================================================
# Geração de dados sintéticos
# =====================================================
# Modo de geração: 'densidade_realista', 'uniforme' ou 'grade'
MODO_GERACAO = 'densidade_realista'

# Semente para todas as operações aleatórias, garantindo reprodutibilidade
SEED = 42

# =====================================================
# Construção do grafo ε‑ball
# =====================================================
# Raio máximo de comunicação entre robôs
RAIO_COMUNICACAO = 50

# =====================================================
# Heurística gulosa e validação
# =====================================================
# Diferença máxima de velocidade permitida para formar cluster
DELTA_V = 5.0

# =====================================================
# Outras configurações
# =====================================================
# Tolerância numérica geral (se precisar)
EPS = 1e-6
