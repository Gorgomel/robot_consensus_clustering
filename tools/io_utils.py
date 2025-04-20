import os
from datetime import datetime

def gerar_nome_pasta(base_dir, base_nome, seed):
    """
    Cria uma pasta dentro de base_dir com nome base_nome_seed.
    Se já existir, pergunta se deseja sobrescrever.
    Se não, cria com timestamp.
    """
    nome_base = f"{base_nome}_seed{seed}"
    path_base = os.path.join(base_dir, nome_base)

    if os.path.exists(path_base):
        resposta = input(f"[?] A pasta '{nome_base}' já existe. Deseja sobrescrever? (s/N): ").strip().lower()
        if resposta != 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_base += f"_{timestamp}"
            path_base = os.path.join(base_dir, nome_base)

    os.makedirs(path_base, exist_ok=True)
    return path_base
