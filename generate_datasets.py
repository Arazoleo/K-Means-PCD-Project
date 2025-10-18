#!/usr/bin/env python3

import numpy as np
import os

def generate_dataset(n_points, n_clusters, filename_prefix):
    print(f"Gerando dataset {filename_prefix} com {n_points:,} pontos e K={n_clusters}")
    
    np.random.seed(42)
    
    cluster_std = 0.8
    cluster_centers = np.linspace(-10, 10, n_clusters)
    
    data = []
    for center in cluster_centers:
        cluster_data = np.random.normal(center, cluster_std, n_points // n_clusters)
        data.extend(cluster_data)
    
    remaining = n_points - len(data)
    if remaining > 0:
        extra_data = np.random.normal(0, 2, remaining)
        data.extend(extra_data)
    
    data = np.array(data)
    np.random.shuffle(data)
    
    dados_filename = f"dados_{filename_prefix}.csv"
    np.savetxt(dados_filename, data, delimiter=',', fmt='%.6f')
    print(f"Dados salvos em: {dados_filename}")
    
    centroides_filename = f"centroides_{filename_prefix}.csv"
    initial_centroids = np.random.uniform(data.min(), data.max(), n_clusters)
    np.savetxt(centroides_filename, initial_centroids, delimiter=',', fmt='%.6f')
    print(f"Centroides salvos em: {centroides_filename}")
    
    return dados_filename, centroides_filename

def main():
    print("=" * 60)
    print("GERADOR DE DATASETS PARA K-MEANS")
    print("=" * 60)
    
    datasets = {
        'pequeno': (10000, 4),
        'medio': (100000, 8), 
        'grande': (1000000, 16)
    }
    
    print(f"Gerando datasets na pasta: {os.getcwd()}")
    print()
    
    generated_files = []
    
    for name, (size, k) in datasets.items():
        dados_file, centroides_file = generate_dataset(size, k, name)
        generated_files.extend([dados_file, centroides_file])
        print()
    
    print("=" * 60)
    print("DATASETS GERADOS COM SUCESSO")
    print("=" * 60)
    print("Arquivos criados:")
    for file in generated_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main()

