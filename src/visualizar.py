import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

caminho_dados = os.path.join(base_dir, 'data', 'sinteticos', 'robos.npy')
saida_dir = os.path.join(base_dir, 'data', 'sinteticos')
os.makedirs(saida_dir, exist_ok=True)

dados = np.load(caminho_dados)

x = dados[:, 0]
y = dados[:, 1]
v = dados[:, 2]
theta = dados[:, 3]
bateria = dados[:, 4]

# Estimativa da área
max_x, max_y = np.max(x), np.max(y)
area_info = f"{int(np.ceil(max_x))}x{int(np.ceil(max_y))}"

# 1. Scatterplot da posição (x, y) com velocidade como cor
plt.figure(figsize=(10, 8))
scatter = plt.scatter(x, y, c=v, cmap='viridis', s=40)
plt.colorbar(scatter, label='Velocidade')
plt.xlabel('Posição X')
plt.ylabel('Posição Y')
plt.title(f'Distribuição Espacial dos Robôs (cor = velocidade)\n[modo: densidade_realista | área: {area_info}]')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'posicoes_velocidade_area_maior.png'))
plt.close()

# 2. Histograma da velocidade
plt.figure(figsize=(6, 4))
sns.histplot(v, bins=20, kde=True, color='blue')
plt.title('Distribuição das Velocidades dos Robôs')
plt.xlabel('Velocidade')
plt.ylabel('Frequência')
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'hist_velocidade_area_maior.png'))
plt.close()

# 3. Histograma da bateria
plt.figure(figsize=(6, 4))
sns.histplot(bateria, bins=20, kde=True, color='green')
plt.title('Distribuição da Bateria dos Robôs')
plt.xlabel('Bateria (%)')
plt.ylabel('Frequência')
plt.tight_layout()
plt.savefig(os.path.join(saida_dir, 'hist_bateria_area_maior.png'))
plt.close()

# 4. Estatísticas resumidas
resumo_path = os.path.join(saida_dir, 'resumo_estatistico_area_maior.txt')
with open(resumo_path, 'w', encoding='utf-8') as f:
    f.write("Resumo estatístico dos atributos dos robôs (modo: densidade_realista)\n\n")
    f.write(f"Total de robôs: {len(dados)}\n")
    f.write(f"Média de velocidade: {np.mean(v):.2f}\n")
    f.write(f"Desvio padrão de velocidade: {np.std(v):.2f}\n\n")
    f.write(f"Média de bateria: {np.mean(bateria):.2f}\n")
    f.write(f"Desvio padrão de bateria: {np.std(bateria):.2f}\n\n")
    f.write(f"Faixa de posição X: {np.min(x):.2f} a {np.max(x):.2f}\n")
    f.write(f"Faixa de posição Y: {np.min(y):.2f} a {np.max(y):.2f}\n")
    f.write(f"Tamanho estimado da área: {area_info}\n")

print("Visualizações e resumo estatístico salvos com sucesso.")
