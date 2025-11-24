#!/bin/bash

detect_mpicc() {
    local arch=$(uname -m)
    local mpicc_candidates=()
    
    if [ "$arch" = "arm64" ]; then
        mpicc_candidates=(
            "/opt/homebrew/bin/mpicc"
            "mpicc"
        )
    else
        mpicc_candidates=(
            "/opt/homebrew/bin/mpicc"
            "/usr/local/bin/mpicc"
            "mpicc"
        )
    fi
    
    for mpicc_cmd in "${mpicc_candidates[@]}"; do
        if [ -f "$mpicc_cmd" ] || command -v "$mpicc_cmd" &> /dev/null; then
            echo "$mpicc_cmd"
            return 0
        fi
    done
    
    echo ""
    return 1
}

MPICC=$(detect_mpicc)

if [ -z "$MPICC" ]; then
    echo "ERRO: Compilador MPI não encontrado!"
    echo "Instale OpenMPI ou MPICH:"
    echo "  macOS: arch -arm64 brew install openmpi"
    echo "  Linux: sudo apt-get install libopenmpi-dev"
    exit 1
fi

ARCH=$(uname -m)
USE_ARCH=""

if [ "$ARCH" = "x86_64" ] && [[ "$OSTYPE" == "darwin"* ]]; then
    echo "AVISO: Terminal em modo Rosetta (x86_64)."
    echo "Usando 'arch -arm64' para compilar e executar em modo nativo ARM64."
    USE_ARCH="arch -arm64"
fi

echo "======================================"
echo "TESTES - VERSÃO MPI"
echo "======================================"
echo "Usando compilador: $MPICC"
echo "Arquitetura: $ARCH"
if [ -n "$USE_ARCH" ]; then
    echo "Modo: $USE_ARCH"
fi
echo ""

echo "Compilando versão MPI..."
$USE_ARCH $MPICC -O2 -std=c99 method_means_1d_mpi.c -o kmeans_1d_mpi -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar!"
    exit 1
fi
echo "Versão MPI compilada"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    NUM_CORES=$(sysctl -n hw.ncpu)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    NUM_CORES=$(nproc)
else
    NUM_CORES=8
fi

echo "Sistema: $OSTYPE"
echo "Cores disponíveis: $NUM_CORES"
echo ""

if [ ! -f "dados_pequeno.csv" ] || [ ! -f "dados_medio.csv" ] || [ ! -f "dados_grande.csv" ]; then
    echo "ERRO: Datasets não encontrados!"
    echo "Execute primeiro: cd .. && python3 generate_datasets.py"
    exit 1
fi

echo "======================================"
echo "Dataset PEQUENO (N=10,000, K=4)"
echo "======================================"
for P in 1 2 4; do
    echo ""
    echo "--- MPI com $P processo(s) ---"
    $USE_ARCH mpirun -np $P ./kmeans_1d_mpi dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_mpi${P}_pequeno.csv centroids_mpi${P}_pequeno.csv
done
echo ""

echo "======================================"
echo "Dataset MÉDIO (N=100,000, K=8)"
echo "======================================"
for P in 1 2 4 8; do
    echo ""
    echo "--- MPI com $P processo(s) ---"
    $USE_ARCH mpirun -np $P ./kmeans_1d_mpi dados_medio.csv centroides_medio.csv 50 0.000001 assign_mpi${P}_medio.csv centroids_mpi${P}_medio.csv
done
echo ""

echo "======================================"
echo "Dataset GRANDE (N=1,000,000, K=16)"
echo "======================================"
for P in 1 2 4 8 16; do
    if [ $P -le $NUM_CORES ]; then
        echo ""
        echo "--- MPI com $P processo(s) ---"
        $USE_ARCH mpirun -np $P ./kmeans_1d_mpi dados_grande.csv centroides_grande.csv 50 0.000001 assign_mpi${P}_grande.csv centroids_mpi${P}_grande.csv
    fi
done
echo ""

echo "======================================"
echo "TESTES CONCLUÍDOS"
echo "======================================"
echo "Resultados salvos em:"
echo "  - mpi/assign_mpi*_*.csv"
echo "  - mpi/centroids_mpi*_*.csv"
echo ""
echo "Para análise detalhada:"
echo "  cd mpi && python3 analyze_results.py"

