# K-Means 1D - Implementação Serial, OpenMP e MPI

Implementação do algoritmo K-means unidimensional com versões serial, paralela OpenMP (memória compartilhada) e distribuída MPI.

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
├── openmp/
│   ├── method_means_1d_omp.c
│   ├── analyze_results.py
│   ├── run_tests.sh
│   └── README.md
└── mpi/
    ├── method_means_1d_mpi.c
    ├── analyze_results.py
    ├── run_tests.sh
    └── README.md
```

## Requisitos

- GCC com suporte a OpenMP
- MPI (OpenMPI ou MPICH) - apenas para versão MPI
- Python 3 com numpy, matplotlib e seaborn

### Instalação no macOS

```bash
brew install gcc openmpi python3
pip3 install numpy matplotlib seaborn
```

### Instalação no Linux

```bash
sudo apt-get install gcc libopenmpi-dev python3 python3-pip
pip3 install numpy matplotlib seaborn
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

### OpenMP com Schedule Runtime

```bash
cd openmp
gcc -O2 -fopenmp -std=c99 method_means_1d_omp_schedule.c -o kmeans_schedule -lm
```

### MPI

```bash
cd mpi
mpicc -O2 -std=c99 method_means_1d_mpi.c -o kmeans_1d_mpi -lm
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

### Testes de Schedule e Chunk Size

Teste diferentes políticas de escalonamento:

```bash
cd openmp
bash test_schedule.sh
```

Este script testa automaticamente:
- Threads: 1, 2, 4, 8, 16
- Schedules: static(1000, 10000), dynamic(1000), guided
- Dataset: grande (N=1M, K=16)

Execução manual com configuração específica:
```bash
cd openmp
export OMP_NUM_THREADS=8
export OMP_SCHEDULE="dynamic,1000"
./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
```

Configurações de schedule disponíveis:
- `static` ou `static,chunk_size`
- `dynamic` ou `dynamic,chunk_size`
- `guided` ou `guided,chunk_size`

Consulte `openmp/README.md` para detalhes.

## Paralelização MPI

Implementação distribuída usando Message Passing Interface (MPI).

### Arquitetura

- **Distribuição de dados:** Processo 0 lê e distribui os N pontos entre P processos usando `MPI_Scatterv`
- **Broadcast:** Todos os processos recebem os centróides C via `MPI_Bcast`
- **Assignment local:** Cada processo calcula `assign_local` e `SSE_local` para seus pontos
- **Redução global:**
  - `MPI_Reduce` para somar `SSE_local → SSE_global` (apenas processo 0)
  - `MPI_Allreduce` para somar `sum_local[c]` e `cnt_local[c]` (todos os processos)
- **Update global:** Todos os processos atualizam C com os resultados globais

### Execução

```bash
cd mpi
bash run_tests.sh
python3 analyze_results.py
```

Este script testa automaticamente:
- Pequeno: 1, 2, 4 processos
- Médio: 1, 2, 4, 8 processos
- Grande: 1, 2, 4, 8, 16 processos

Execução manual:
```bash
cd mpi
mpirun -np 4 ./kmeans_1d_mpi dados_grande.csv centroides_grande.csv 50 0.000001
```

### Medições

- **Strong scaling:** P ∈ {1, 2, 4, 8, 16} processos
- **Tempo de comunicação:** Overhead de `MPI_Allreduce` (2 por iteração)
- **Speedup:** Comparação com versão serial e OpenMP
- **Eficiência paralela:** Avaliação do overhead de comunicação

Consulte `mpi/README.md` para detalhes completos.

