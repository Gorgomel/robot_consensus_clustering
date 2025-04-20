import os
import numpy as np

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
raw_dir = os.path.join(base_dir, 'data', 'Reddit', 'raw')
saida_dir = os.path.join(base_dir, 'data', 'Reddit', 'processed')
os.makedirs(saida_dir, exist_ok=True)

reddit_data = np.load(os.path.join(raw_dir, 'reddit_data.npz'))
reddit_graph = np.load(os.path.join(raw_dir, 'reddit_graph.npz'))

x = reddit_data['feature']
y = reddit_data['label']
ids = reddit_data['node_ids']

n_sub = 5000
x_sub = x[:n_sub]
y_sub = y[:n_sub]
ids_sub = ids[:n_sub]

row = reddit_graph['row']
col = reddit_graph['col']
mask = (row < n_sub) & (col < n_sub)
row_sub = row[mask]
col_sub = col[mask]

np.savez(os.path.join(saida_dir, 'reddit_5k.npz'),
         feature=x_sub,
         label=y_sub,
         node_ids=ids_sub,
         edge_index=np.vstack((row_sub, col_sub)))

print("reddit_5k.npz salvo com sucesso em data/Reddit/processed")
