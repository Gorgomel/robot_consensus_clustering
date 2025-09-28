#!/bin/bash

PROJECT_PATH="/mnt/c/Users/Brunn/Desktop/PA-Novo"
VENV_PATH="/mnt/c/Users/Brunn/Desktop/.venv"

cd "$PROJECT_PATH" || { echo "Caminho inválido: $PROJECT_PATH"; exit 1; }

if [ -f "$VENV_PATH/bin/activate" ]; then
  source "$VENV_PATH/bin/activate"
  echo "[INFO] Ambiente virtual ativado"
else
  echo "[WARNING] Ambiente virtual não encontrado em $VENV_PATH"
fi

exec bash  # mantém terminal aberto

code .
