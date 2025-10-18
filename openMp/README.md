# K-Means 1D - Versão OpenMP

Implementação paralela do algoritmo K-means unidimensional usando OpenMP.

## Requisitos

- GCC com suporte a OpenMP
- Python 3 com numpy e matplotlib

## Compilação

### macOS

```bash
gcc-15 -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
```

Se não tiver gcc-15:
```bash
brew install gcc
```

### Linux

```bash
gcc -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
```

## Como Executar

### Passo 1: Gerar Datasets

Na raiz do projeto:

```bash
cd ..
python3 generate_datasets.py
cd openmp
```

### Passo 2: Executar Testes

```bash
bash run_tests.sh
```

Este script:
1. Detecta o compilador GCC com suporte OpenMP
2. Compila a versão OpenMP
3. Verifica se os datasets existem
4. Executa testes com 1, 2, 4, 8 e 16 threads
5. Testa os três datasets:
   - Pequeno: N=10.000, K=4
   - Médio: N=100.000, K=8
   - Grande: N=1.000.000, K=16
6. Salva resultados em assign_omp*_*.csv e centroids_omp*_*.csv

### Passo 3: Analisar Resultados

```bash
python3 analyze_results.py
```

Gera:
- performance_analysis_openmp.png
- Gráficos de tempo e speedup
- Relatório comparativo no terminal

## Execução Manual

```bash
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign.csv centroids.csv
```

Parâmetros:
1. Arquivo de dados
2. Arquivo de centróides iniciais
3. Número máximo de iterações
4. Epsilon para convergência
5. Arquivo de saída para atribuições
6. Arquivo de saída para centróides finais

Controle o número de threads via variável OMP_NUM_THREADS.

## Paralelização

### Assignment Step
```c
#pragma omp parallel for reduction(+:sse)
```
Cada thread processa um subconjunto dos N pontos.

### Update Step
Acumuladores locais por thread com redução em região crítica.

## Formato dos Arquivos

CSV com uma coluna, sem cabeçalho.

Entrada:
```
1.234567
2.345678
```

Saída:
```
0
1
```

## Saída no Terminal

```
K-means 1D (OpenMP)
Threads: 4
N=10000 K=4 max_iter=50 eps=1e-06
Iterações: 12 | SSE final: 61203.756968 | Tempo: 1.8 ms
```
