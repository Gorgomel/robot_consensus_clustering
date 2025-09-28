#!/bin/bash
# Este script foi criado no Windows


# Caminho no Windows
SRC="/mnt/c/Users/Brunn/Desktop/PA-Novo"

# Caminho de destino no WSL
DEST="$HOME/PA-Novo"

# Cria o diretório de destino se não existir
mkdir -p "$DEST"

# Sincroniza com rsync (preserva estrutura, atualiza modificados, exclui removidos)
rsync -av --delete --exclude 'venv/' --exclude '__pycache__/' "$SRC/" "$DEST/"

echo "✅ Projeto sincronizado para: $DEST"
