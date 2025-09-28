#!/bin/bash
# Este script foi criado no Linux/WSL
# Caminho absoluto do diretório do projeto no Windows
PROJETO_WIN="/mnt/c/Users/Brunn/Desktop/PA-Novo"

# Caminho de backup dentro do WSL (opcional, você pode mudar para outra pasta externa)
BACKUP_WSL="$HOME/PA-Novo-backup"

# Cria o diretório de destino, se não existir
mkdir -p "$BACKUP_WSL"

echo "🔄 Sincronizando do projeto do Windows para backup WSL..."
rsync -av --exclude 'venv/' --exclude '__pycache__/' --exclude '*.npy' \
  "$PROJETO_WIN"/ "$BACKUP_WSL"

echo "✅ Projeto do Windows sincronizado com backup em: $BACKUP_WSL"
