# K-Means 1D - Implementação Serial e OpenMP

Implementação do algoritmo K-means unidimensional com versões serial e paralela OpenMP.

## Estrutura do Projeto

```
K-Means-PCD-Project/
├── generate_datasets.py
├── run_all_tests.sh
├── README.md
├── serial/
│   ├── method_means_1d_serial.c
│   ├── analyze_results.py
│   ├── run_tests.sh
│   └── README.md
└── openmp/
    ├── method_means_1d_omp.c
    ├── analyze_results.py
    ├── run_tests.sh
    └── README.md
```

## Requisitos

- GCC com suporte a OpenMP
- Python 3 com numpy, matplotlib e seaborn

### Instalação no macOS

```bash
brew install gcc python3
pip3 install numpy matplotlib seaborn
```

### Instalação no Linux

```bash
sudo apt-get install gcc python3 python3-pip
pip3 install numpy matplotlib
```

## Como Executar

### Execução Completa

Na raiz do projeto:

```bash
bash run_all_tests.sh
```

Este script executa:
1. Geração de datasets (se não existirem)
2. Compilação das versões serial e OpenMP
3. Criação de links simbólicos para datasets
4. Testes da versão serial nos 3 datasets
5. Testes da versão OpenMP com 1, 2, 4, 8 e 16 threads nos 3 datasets

### Geração Manual de Datasets

```bash
python3 generate_datasets.py
```

Gera três datasets:
- dados_pequeno.csv: N=10.000 pontos, K=4 clusters
- dados_medio.csv: N=100.000 pontos, K=8 clusters
- dados_grande.csv: N=1.000.000 pontos, K=16 clusters

### Execução Individual por Versão

#### Versão Serial

```bash
cd serial
bash run_tests.sh
python3 analyze_results.py
```

#### Versão OpenMP

```bash
cd openmp
bash run_tests.sh
python3 analyze_results.py
```

## Compilação Manual

### Serial

```bash
cd serial
gcc -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm
```

### OpenMP

```bash
cd openmp
gcc -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
```

## Formato dos Arquivos

Todos os CSV têm uma coluna, sem cabeçalho.

Entrada:
```
1.234567
2.345678
3.456789
```

Saída (assign.csv):
```
0
1
0
```

Saída (centroids.csv):
```
15.234567
25.123456
```

## Algoritmo

### Assignment Step
Para cada ponto, encontra o centróide mais próximo.

### Update Step
Calcula a média dos pontos de cada cluster.
Clusters vazios recebem o primeiro ponto.


## Paralelização OpenMP

- Assignment: `#pragma omp parallel for reduction(+:sse)`
- Update: acumuladores locais por thread com redução crítica

