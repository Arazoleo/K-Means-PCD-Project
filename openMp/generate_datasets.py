#!/usr/bin/env python3

import numpy as np
import os

def generate_dataset(n_points, filename_prefix):
    """
    Gera datasets de dados e centroides para testes do K-means
    
    Args:
        n_points: Número de pontos de dados
        filename_prefix: Prefixo para os nomes dos arquivos (ex: 'pequeno', 'medio', 'grande')
    """
    
    print(f"Gerando dataset {filename_prefix} com {n_points:,} pontos...")
    
    # Gerar dados aleatórios com distribuição normal
    np.random.seed(42)  # Para reprodutibilidade
    
    # Criar clusters artificiais
    cluster_centers = np.array([-5, -2, 0, 2, 5])
    cluster_std = 0.8
    
    data = []
    for center in cluster_centers:
        cluster_data = np.random.normal(center, cluster_std, n_points // len(cluster_centers))
        data.extend(cluster_data)
    
    # Adicionar pontos extras se necessário
    remaining = n_points - len(data)
    if remaining > 0:
        extra_data = np.random.normal(0, 2, remaining)
        data.extend(extra_data)
    
    # Embaralhar os dados
    data = np.array(data)
    np.random.shuffle(data)
    
    # Salvar dados
    dados_filename = f"dados_{filename_prefix}.csv"
    np.savetxt(dados_filename, data, delimiter=',', fmt='%.6f')
    print(f"✓ Dados salvos em: {dados_filename}")
    
    # Gerar centroides iniciais aleatórios
    centroides_filename = f"centroides_{filename_prefix}.csv"
    initial_centroids = np.random.uniform(data.min(), data.max(), 5)
    np.savetxt(centroides_filename, initial_centroids, delimiter=',', fmt='%.6f')
    print(f"✓ Centroides salvos em: {centroides_filename}")
    
    return dados_filename, centroides_filename

def main():
    """
    Gera todos os datasets necessários para os testes
    """
    print("=" * 60)
    print("GERADOR DE DATASETS PARA K-MEANS")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('run_tests.sh'):
        print("ERRO: Execute este script dentro da pasta openMp/")
        return
    
    # Definir tamanhos dos datasets
    datasets = {
        'pequeno': 10000,
        'medio': 100000, 
        'grande': 1000000
    }
    
    print(f"Gerando datasets na pasta atual: {os.getcwd()}")
    print()
    
    generated_files = []
    
    for name, size in datasets.items():
        dados_file, centroides_file = generate_dataset(size, name)
        generated_files.extend([dados_file, centroides_file])
        print()
    
    print("=" * 60)
    print("DATASETS GERADOS COM SUCESSO!")
    print("=" * 60)
    print("Arquivos criados:")
    for file in generated_files:
        print(f"  - {file}")
    
    print()
    print("Agora você pode executar: bash run_tests.sh")

if __name__ == "__main__":
    main()
