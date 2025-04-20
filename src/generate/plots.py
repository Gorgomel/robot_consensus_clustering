# src/plots.py
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_histogram(data, bins, title, xlabel, ylabel, out_path, density=False):
    plt.figure(figsize=(6,4))
    plt.hist(data, bins=bins, density=density, edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_scatter(x, y, c=None, cmap='viridis', title='', xlabel='', ylabel='', out_path=None):
    plt.figure(figsize=(8,6))
    sc = plt.scatter(x, y, c=c, cmap=cmap, s=10)
    if c is not None:
        plt.colorbar(sc)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    if out_path:
        plt.savefig(out_path)
        plt.close()

def plot_heatmap(matrix, title, xlabel, ylabel, cbar_label, out_path):
    plt.figure(figsize=(6,6))
    im = plt.imshow(matrix, origin='lower', cmap='inferno')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    cbar = plt.colorbar(im)
    cbar.set_label(cbar_label)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
