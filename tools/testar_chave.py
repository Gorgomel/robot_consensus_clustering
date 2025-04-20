import numpy as np
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
raw_dir = os.path.join(base_dir, 'data', 'Reddit', 'raw')

reddit_data = np.load(os.path.join(raw_dir, 'reddit_data.npz'))
reddit_graph = np.load(os.path.join(raw_dir, 'reddit_graph.npz'))

print("=== reddit_data.npz ===")
print(reddit_data.files)

print("\n=== reddit_graph.npz ===")
print(reddit_graph.files)
