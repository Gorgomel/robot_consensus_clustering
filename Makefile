SHELL := bash

PYTHON := PYTHONPATH=. python3

# Parâmetros padrão (podem ser sobrescritos na linha de comando)
SEED             ?= 42
NUM_ROBOS        ?= 10000
LADO             ?= 3000
RAIO_COMUNICACAO ?= 50
METHOD           ?= guloso_fo1

.PHONY: all data graph cluster evaluate clean \
        create-venv-wsl create-venv-win sync-wsl sync-win

all: data graph cluster evaluate

# 1) Geração de dados
data:
	@echo "\n[make] Gerando dados sintéticos (n=$(NUM_ROBOS), lado=$(LADO), seed=$(SEED))..."
	$(PYTHON) src/pipeline.py generate \
		--num-robos $(NUM_ROBOS) \
		--lado $(LADO) \
		--seed $(SEED)

# 2) Construção do grafo ε-ball
graph:
	@echo "\n[make] Construindo grafo ε-ball (ε=$(RAIO_COMUNICACAO))..."
	$(PYTHON) src/pipeline.py build-graph \
		--num-robos $(NUM_ROBOS) \
		--seed $(SEED) \
		--raio $(RAIO_COMUNICACAO)

# 3) Clusterização (guloso, local search, meta)
cluster:
	@echo "\n[make] Rodando heurísticas (method=$(METHOD))..."
	$(PYTHON) src/pipeline.py cluster \
		--method $(METHOD) \
		--num-robos $(NUM_ROBOS) \
		--seed $(SEED)

# 4) Avaliação final
evaluate:
	@echo "\n[make] Avaliando resultados e gerando relatórios..."
	$(PYTHON) src/pipeline.py evaluate

# Ambiente virtual no WSL
create-venv-wsl:
	@echo "\n[make] Criando venv WSL em ~/.venvs/PA-Novo..."
	$(PYTHON) -m venv ~/.venvs/PA-Novo
	source ~/.venvs/PA-Novo/bin/activate && pip install -r requirements.txt

# Ambiente virtual no Windows
create-venv-win:
	@echo "\n[make] Criando venv Windows em ./venv..."
	python -m venv venv
	venv\Scripts\activate.bat && pip install -r requirements.txt

# Sincronizar: WSL → Windows
sync-win:
	@echo "\n[make] Sincronizando alterações para Windows..."
	bash tools/sync_to_windows.sh

# Sincronizar: Windows → WSL
sync-wsl:
	@echo "\n[make] Sincronizando alterações para WSL..."
	bash tools/sync_to_wsl.sh

# Limpeza geral
clean:
	@echo "\n[make] Limpando diretórios de saída..."
	rm -rf data/sinteticos/* data/grafo/* data/cluster/* data/plots/*
