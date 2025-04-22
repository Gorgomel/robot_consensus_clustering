# src/tools/io_utils.py
import os
from datetime import datetime

def gerar_nome_pasta(seed, num_robos, base="robos"):
    """
    Retorna o nome da pasta onde os dados sintéticos foram gerados,
    no formato '{base}_{num_robos}_seed{seed}[_timestamp]'.
    Se já existir, adiciona um timestamp para não sobrescrever.
    """
    nome_base = f"{base}_{num_robos}_seed{seed}"
    if os.path.exists(os.path.join("data", "sinteticos", nome_base)):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base += f"_{ts}"
    return nome_base
