#!/bin/bash
# Script para testar o desempenho do K-means com diferentes configurações

echo "======================================"
echo "Compilando as versões..."
echo "======================================"

# Compilar versão serial
/opt/homebrew/bin/gcc-15 -O2 -std=c99 kmeans_1d_serial.c -o kmeans_1d_serial -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão serial!"
    exit 1
fi
echo "✓ Versão serial compilada"

# Compilar versão OpenMP
/opt/homebrew/bin/gcc-15 -O2 -fopenmp -std=c99 kmeans_1d_omp.c -o kmeans_1d_omp -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão OpenMP!"
    exit 1
fi
echo "✓ Versão OpenMP compilada"

echo ""
echo "======================================"
echo "Testando Dataset PEQUENO (N=10,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001

echo ""
echo "======================================"
echo "Testando Dataset MÉDIO (N=100,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_medio.csv centroides_medio.csv 50 0.000001

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001

echo ""
echo "======================================"
echo "Testando Dataset GRANDE (N=1,000,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_grande.csv centroides_grande.csv 50 0.000001

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001

echo ""
echo "======================================"
echo "Testes concluídos!"
echo "======================================"
