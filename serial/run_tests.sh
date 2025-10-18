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
echo "K-means 1D - Testes Versão Serial"
echo "======================================"
echo "Usando compilador: $GCC"
echo ""

echo "======================================"
echo "Compilando versão serial..."
echo "======================================"

$GCC -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
if [ $? -ne 0 ]; then
    echo "Erro ao compilar versão serial!"
    exit 1
fi
echo "Versão serial compilada"

echo ""
echo "======================================"
echo "Verificando datasets..."
echo "======================================"

if [ ! -f "dados_pequeno.csv" ] || [ ! -f "dados_medio.csv" ] || [ ! -f "dados_grande.csv" ]; then
    echo "ERRO: Datasets não encontrados!"
    echo "Execute primeiro na raiz do projeto: python3 generate_datasets.py"
    echo "Ou execute: bash run_all_tests.sh"
    exit 1
fi
echo "Datasets encontrados"

echo ""
echo "======================================"
echo "Testando Dataset PEQUENO (N=10,000, K=4)"
echo "======================================"
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_serial_pequeno.csv centroids_serial_pequeno.csv

echo ""
echo "======================================"
echo "Testando Dataset MÉDIO (N=100,000, K=8)"
echo "======================================"
./kmeans_1d_serial dados_medio.csv centroides_medio.csv 50 0.000001 assign_serial_medio.csv centroids_serial_medio.csv

echo ""
echo "======================================"
echo "Testando Dataset GRANDE (N=1,000,000, K=16)"
echo "======================================"
./kmeans_1d_serial dados_grande.csv centroides_grande.csv 50 0.000001 assign_serial_grande.csv centroids_serial_grande.csv

echo ""
echo "======================================"
echo "Testes concluídos!"
echo "======================================"
echo ""
echo "Arquivos gerados:"
echo "  - assign_serial_*.csv (atribuições de cluster)"
echo "  - centroids_serial_*.csv (centróides finais)"
echo ""
echo "Para análise detalhada, execute:"
echo "  python3 analyze_results.py"

