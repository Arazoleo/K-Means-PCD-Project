#!/bin/bash

detect_gcc() {
    local gcc_candidates=(
        "gcc-15"
        "gcc-14"
        "gcc-13"
        "gcc-12"
        "gcc-11"
        "gcc"
    )
    
    if [ -f "/opt/homebrew/bin/gcc-15" ]; then
        echo "/opt/homebrew/bin/gcc-15"
        return 0
    fi
    
    for gcc_cmd in "${gcc_candidates[@]}"; do
        if [ -f "/usr/local/bin/$gcc_cmd" ]; then
            echo "/usr/local/bin/$gcc_cmd"
            return 0
        fi
    done
    
    for gcc_cmd in "${gcc_candidates[@]}"; do
        if command -v "$gcc_cmd" &> /dev/null; then
            echo "$gcc_cmd"
            return 0
        fi
    done
    
    echo ""
    return 1
}

GCC=$(detect_gcc)

if [ -z "$GCC" ]; then
    echo "ERRO: Compilador GCC não encontrado!"
    echo "Por favor, instale o GCC:"
    echo "  - macOS: brew install gcc"
    echo "  - Ubuntu/Debian: sudo apt-get install gcc"
    echo "  - Fedora: sudo dnf install gcc"
    exit 1
fi

echo "======================================"
echo "Usando compilador: $GCC"
echo "======================================"

echo "Verificando suporte a OpenMP..."
$GCC -fopenmp -dM -E - < /dev/null 2>/dev/null | grep -q "_OPENMP"
if [ $? -ne 0 ]; then
    echo "AVISO: OpenMP pode não estar disponível com este compilador"
fi

echo ""
echo "======================================"
echo "Compilando as versões..."
echo "======================================"

$GCC -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão serial!"
    exit 1
fi
echo "✓ Versão serial compilada"

$GCC -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão OpenMP!"
    exit 1
fi
echo "✓ Versão OpenMP compilada"

if [[ "$OSTYPE" == "darwin"* ]]; then
    NUM_CORES=$(sysctl -n hw.ncpu)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    NUM_CORES=$(nproc)
else
    NUM_CORES=8
fi

echo "Sistema detectado: $OSTYPE"
echo "Número de cores disponíveis: $NUM_CORES"

echo ""
echo "======================================"
echo "Gerando datasets..."
echo "======================================"

# Verificar se os datasets já existem
if [ ! -f "dados_pequeno.csv" ] || [ ! -f "dados_medio.csv" ] || [ ! -f "dados_grande.csv" ]; then
    echo "Gerando datasets necessários..."
    python3 generate_datasets.py
    if [ $? -ne 0 ]; then
        echo "Erro ao gerar datasets!"
        exit 1
    fi
    echo "✓ Datasets gerados com sucesso"
else
    echo "✓ Datasets já existem, pulando geração"
fi

echo ""
echo "======================================"
echo "Testando Dataset PEQUENO (N=10,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_serial_pequeno.csv centroids_serial_pequeno.csv

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp1_pequeno.csv centroids_omp1_pequeno.csv

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp2_pequeno.csv centroids_omp2_pequeno.csv

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp4_pequeno.csv centroids_omp4_pequeno.csv

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp8_pequeno.csv centroids_omp8_pequeno.csv

echo ""
echo "--- OpenMP (16 threads) ---"
export OMP_NUM_THREADS=16
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp16_pequeno.csv centroids_omp16_pequeno.csv

echo ""
echo "======================================"
echo "Testando Dataset MÉDIO (N=100,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_medio.csv centroides_medio.csv 50 0.000001 assign_serial_medio.csv centroids_serial_medio.csv

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp1_medio.csv centroids_omp1_medio.csv

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp2_medio.csv centroids_omp2_medio.csv

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp4_medio.csv centroids_omp4_medio.csv

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp8_medio.csv centroids_omp8_medio.csv

echo ""
echo "--- OpenMP (16 threads) ---"
export OMP_NUM_THREADS=16
./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp16_medio.csv centroids_omp16_medio.csv

echo ""
echo "======================================"
echo "Testando Dataset GRANDE (N=1,000,000)"
echo "======================================"

echo ""
echo "--- SERIAL ---"
./kmeans_1d_serial dados_grande.csv centroides_grande.csv 50 0.000001 assign_serial_grande.csv centroids_serial_grande.csv

echo ""
echo "--- OpenMP (1 thread) ---"
export OMP_NUM_THREADS=1
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp1_grande.csv centroids_omp1_grande.csv

echo ""
echo "--- OpenMP (2 threads) ---"
export OMP_NUM_THREADS=2
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp2_grande.csv centroids_omp2_grande.csv

echo ""
echo "--- OpenMP (4 threads) ---"
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp4_grande.csv centroids_omp4_grande.csv

echo ""
echo "--- OpenMP (8 threads) ---"
export OMP_NUM_THREADS=8
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp8_grande.csv centroids_omp8_grande.csv

echo ""
echo "--- OpenMP (16 threads) ---"
export OMP_NUM_THREADS=16
./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp16_grande.csv centroids_omp16_grande.csv

echo ""
echo "======================================"
echo "Testes concluídos!"
echo "======================================"