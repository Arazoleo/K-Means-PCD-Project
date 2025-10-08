#!/usr/bin/env python3

import numpy as np
import sys

def generate_dataset(n_points, n_clusters, output_file, seed=42):
    np.random.seed(seed)
    cluster_centers = np.linspace(10, 100, n_clusters)
    points_per_cluster = n_points // n_clusters
    remaining = n_points % n_clusters
    all_points = []
    
    for i, center in enumerate(cluster_centers):
        n = points_per_cluster + (1 if i < remaining else 0)
        cluster_points = np.random.normal(center, 2.0, n)
        all_points.extend(cluster_points)
    
    np.random.shuffle(all_points)
    
    with open(output_file, 'w') as f:
        for point in all_points:
            f.write(f"{point:.6f}\n")
    
    print(f"Dataset gerado: {output_file}")
    print(f"  - Pontos: {n_points}")
    print(f"  - Clusters: {n_clusters}")
    print(f"  - Centros teóricos: {cluster_centers}")

def generate_initial_centroids(n_clusters, output_file):
    centroids = np.linspace(15, 95, n_clusters)
    
    with open(output_file, 'w') as f:
        for centroid in centroids:
            f.write(f"{centroid:.6f}\n")
    
    print(f"Centróides iniciais gerados: {output_file}")
    print(f"  - Valores: {centroids}")

if __name__ == "__main__":
    print("=== Gerando dataset PEQUENO ===")
    generate_dataset(10000, 4, "dados_pequeno.csv")
    generate_initial_centroids(4, "centroides_pequeno.csv")
    print()
    
    print("=== Gerando dataset MÉDIO ===")
    generate_dataset(100000, 8, "dados_medio.csv")
    generate_initial_centroids(8, "centroides_medio.csv")
    print()
    
    print("=== Gerando dataset GRANDE ===")
    generate_dataset(1000000, 16, "dados_grande.csv")
    generate_initial_centroids(16, "centroides_grande.csv")
    print()
    
    print("Todos os datasets foram gerados com sucesso!")
