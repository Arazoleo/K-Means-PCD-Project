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
    exit 1
fi

echo "======================================"
echo "Testes de Schedule e Chunk Size"
echo "======================================"
echo "Usando compilador: $GCC"
echo ""

echo "Compilando versão com schedule runtime..."
$GCC -O2 -fopenmp -std=c99 method_means_1d_omp_schedule.c -o kmeans_schedule -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar!"
    exit 1
fi
echo "Compilado com sucesso"
echo ""

if [ ! -f "dados_grande.csv" ]; then
    echo "ERRO: Dataset grande não encontrado!"
    echo "Execute primeiro: cd .. && python3 generate_datasets.py"
    exit 1
fi

for THREADS in 1 2 4 8 16; do
    export OMP_NUM_THREADS=$THREADS
    
    echo "======================================"
    echo "Testando com $THREADS thread(s)"
    echo "Dataset: GRANDE (N=1,000,000, K=16)"
    echo "======================================"
    echo ""
    
    echo "--- Schedule: static, chunk=1000 ---"
    export OMP_SCHEDULE="static,1000"
    ./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
    echo ""
    
    echo "--- Schedule: static, chunk=10000 ---"
    export OMP_SCHEDULE="static,10000"
    ./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
    echo ""
    
    echo "--- Schedule: dynamic, chunk=1000 ---"
    export OMP_SCHEDULE="dynamic,1000"
    ./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
    echo ""
    
    echo "--- Schedule: guided ---"
    export OMP_SCHEDULE="guided"
    ./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
    echo ""
done

echo "======================================"
echo "Testes de Schedule Concluídos"
echo "======================================"
echo ""
echo "Configurações testadas:"
echo "  - Threads: 1, 2, 4, 8, 16"
echo "  - Schedules: static(1000, 10000), dynamic(1000), guided"
echo ""


