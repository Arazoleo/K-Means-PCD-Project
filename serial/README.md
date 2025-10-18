# K-Means 1D - Versão Serial

Implementação serial do algoritmo K-means unidimensional.

## Requisitos

- GCC
- Python 3 com numpy e matplotlib

## Compilação

### macOS

```bash
gcc-15 -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
```

Se não tiver gcc-15:
```bash
brew install gcc
```

### Linux

```bash
gcc -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
```

## Como Executar

### Passo 1: Gerar Datasets

Na raiz do projeto:

```bash
cd ..
python3 generate_datasets.py
cd serial
```

### Passo 2: Executar Testes

```bash
bash run_tests.sh
```

Este script:
1. Detecta o compilador GCC disponível
2. Compila a versão serial
3. Verifica se os datasets existem
4. Executa testes nos três datasets:
   - Pequeno: N=10.000, K=4
   - Médio: N=100.000, K=8
   - Grande: N=1.000.000, K=16
5. Salva resultados em assign_serial_*.csv e centroids_serial_*.csv

### Passo 3: Analisar Resultados

```bash
python3 analyze_results.py
```

Gera:
- performance_analysis_serial.png
- Relatório de desempenho no terminal

## Execução Manual

```bash
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign.csv centroids.csv
```

Parâmetros:
1. Arquivo de dados
2. Arquivo de centróides iniciais
3. Número máximo de iterações
4. Epsilon para convergência
5. Arquivo de saída para atribuições
6. Arquivo de saída para centróides finais

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
K-means 1D (SERIAL)
N=10000 K=4 max_iter=50 eps=1e-06
Iterações: 12 | SSE final: 61203.756968 | Tempo: 1.6 ms
```
