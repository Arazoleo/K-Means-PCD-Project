#!/usr/bin/env python3
"""
Script para gerar datasets de teste para K-means 1D
Gera dados com clusters bem definidos em diferentes faixas
"""

import numpy as np
import sys

def generate_dataset(n_points, n_clusters, output_file, seed=42):
    """
    Gera um dataset 1D com clusters bem definidos
    
    Args:
        n_points: número total de pontos
        n_clusters: número de clusters
        output_file: arquivo de saída CSV
        seed: semente para reprodutibilidade
    """
    np.random.seed(seed)
    
    # Definir centros dos clusters espaçados
    cluster_centers = np.linspace(10, 100, n_clusters)
    
    # Gerar pontos ao redor de cada centro
    points_per_cluster = n_points // n_clusters
    remaining = n_points % n_clusters
    
    all_points = []
    
    for i, center in enumerate(cluster_centers):
        # Adicionar pontos extras aos primeiros clusters
        n = points_per_cluster + (1 if i < remaining else 0)
        
        # Gerar pontos com distribuição normal ao redor do centro
        # Desvio padrão de 2.0 para manter clusters separados
        cluster_points = np.random.normal(center, 2.0, n)
        all_points.extend(cluster_points)
    
    # Embaralhar os pontos
    np.random.shuffle(all_points)
    
    # Salvar no arquivo CSV
    with open(output_file, 'w') as f:
        for point in all_points:
            f.write(f"{point:.6f}\n")
    
    print(f"Dataset gerado: {output_file}")
    print(f"  - Pontos: {n_points}")
    print(f"  - Clusters: {n_clusters}")
    print(f"  - Centros teóricos: {cluster_centers}")

def generate_initial_centroids(n_clusters, output_file):
    """
    Gera centróides iniciais para K-means
    Usa valores espaçados uniformemente
    
    Args:
        n_clusters: número de clusters
        output_file: arquivo de saída CSV
    """
    # Centróides iniciais ligeiramente deslocados dos centros reais
    # para que o algoritmo tenha trabalho a fazer
    centroids = np.linspace(15, 95, n_clusters)
    
    with open(output_file, 'w') as f:
        for centroid in centroids:
            f.write(f"{centroid:.6f}\n")
    
    print(f"Centróides iniciais gerados: {output_file}")
    print(f"  - Valores: {centroids}")

if __name__ == "__main__":
    # Pequeno: N=10^4, K=4
    print("=== Gerando dataset PEQUENO ===")
    generate_dataset(10000, 4, "dados_pequeno.csv")
    generate_initial_centroids(4, "centroides_pequeno.csv")
    print()
    
    # Médio: N=10^5, K=8
    print("=== Gerando dataset MÉDIO ===")
    generate_dataset(100000, 8, "dados_medio.csv")
    generate_initial_centroids(8, "centroides_medio.csv")
    print()
    
    # Grande: N=10^6, K=16
    print("=== Gerando dataset GRANDE ===")
    generate_dataset(1000000, 16, "dados_grande.csv")
    generate_initial_centroids(16, "centroides_grande.csv")
    print()
    
    print("Todos os datasets foram gerados com sucesso!")
