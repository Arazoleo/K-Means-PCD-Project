#!/bin/bash

PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

echo "======================================"
echo "K-means 1D - Testes Completos"
echo "======================================"
echo "Diretório do projeto: $PROJECT_ROOT"
echo ""

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

echo "Usando compilador: $GCC"
echo ""

echo "======================================"
echo "Gerando datasets globais..."
echo "======================================"

if [ ! -f "dados_pequeno.csv" ] || [ ! -f "dados_medio.csv" ] || [ ! -f "dados_grande.csv" ]; then
    python3 generate_datasets.py
    if [ $? -ne 0 ]; then
        echo "Erro ao gerar datasets!"
        exit 1
    fi
    echo "Datasets gerados com sucesso"
else
    echo "Datasets já existem"
fi

echo ""
echo "======================================"
echo "Criando links simbólicos..."
echo "======================================"

for dataset in dados_*.csv centroides_*.csv; do
    if [ -f "$dataset" ]; then
        if [ ! -e "serial/$dataset" ]; then
            ln -sf "../$dataset" "serial/$dataset"
        fi
        if [ ! -e "openmp/$dataset" ]; then
            ln -sf "../$dataset" "openmp/$dataset"
        fi
    fi
done

echo "Links criados em serial/ e openmp/"

echo ""
echo "======================================"
echo "Compilando versões..."
echo "======================================"

cd "$PROJECT_ROOT/serial"
$GCC -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão serial!"
    exit 1
fi
echo "Versão serial compilada"

cd "$PROJECT_ROOT/openmp"
$GCC -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão OpenMP!"
    exit 1
fi
echo "Versão OpenMP compilada"

if [[ "$OSTYPE" == "darwin"* ]]; then
    NUM_CORES=$(sysctl -n hw.ncpu)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    NUM_CORES=$(nproc)
else
    NUM_CORES=8
fi

echo ""
echo "Sistema: $OSTYPE"
echo "Cores disponíveis: $NUM_CORES"

echo ""
echo "======================================"
echo "TESTES - VERSÃO SERIAL"
echo "======================================"

cd "$PROJECT_ROOT/serial"

echo ""
echo "Dataset PEQUENO (N=10,000, K=4)"
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_serial_pequeno.csv centroids_serial_pequeno.csv

echo ""
echo "Dataset MÉDIO (N=100,000, K=8)"
./kmeans_1d_serial dados_medio.csv centroides_medio.csv 50 0.000001 assign_serial_medio.csv centroids_serial_medio.csv

echo ""
echo "Dataset GRANDE (N=1,000,000, K=16)"
./kmeans_1d_serial dados_grande.csv centroides_grande.csv 50 0.000001 assign_serial_grande.csv centroids_serial_grande.csv

echo ""
echo "======================================"
echo "TESTES - VERSÃO OPENMP"
echo "======================================"

cd "$PROJECT_ROOT/openmp"

for THREADS in 1 2 4 8 16; do
    echo ""
    echo "======================================"
    echo "OpenMP com $THREADS thread(s)"
    echo "======================================"
    export OMP_NUM_THREADS=$THREADS
    
    echo ""
    echo "Dataset PEQUENO (N=10,000, K=4)"
    ./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp${THREADS}_pequeno.csv centroids_omp${THREADS}_pequeno.csv
    
    echo ""
    echo "Dataset MÉDIO (N=100,000, K=8)"
    ./kmeans_1d_omp dados_medio.csv centroides_medio.csv 50 0.000001 assign_omp${THREADS}_medio.csv centroids_omp${THREADS}_medio.csv
    
    echo ""
    echo "Dataset GRANDE (N=1,000,000, K=16)"
    ./kmeans_1d_omp dados_grande.csv centroides_grande.csv 50 0.000001 assign_omp${THREADS}_grande.csv centroids_omp${THREADS}_grande.csv
done

cd "$PROJECT_ROOT"

echo ""
echo "======================================"
echo "TESTES CONCLUÍDOS"
echo "======================================"
echo ""
echo "Resultados salvos em:"
echo "  - serial/assign_serial_*.csv"
echo "  - serial/centroids_serial_*.csv"
echo "  - openmp/assign_omp*_*.csv"
echo "  - openmp/centroids_omp*_*.csv"
echo ""
echo "Para análise detalhada:"
echo "  cd serial && python3 analyze_results.py"
echo "  cd openmp && python3 analyze_results.py"

