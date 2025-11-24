# K-Means 1D - Versão MPI

Implementação distribuída do algoritmo K-means unidimensional usando MPI (Message Passing Interface).

## Requisitos

- MPI (OpenMPI ou MPICH)
- Python 3 com numpy e matplotlib

## Instalação do MPI

### macOS

```bash
brew install openmpi
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install libopenmpi-dev
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install openmpi-devel
```

## Compilação

```bash
cd mpi
mpicc -O2 -std=c99 method_means_1d_mpi.c -o kmeans_1d_mpi -lm
```

## Como Executar

### Passo 1: Gerar Datasets

Na raiz do projeto:

```bash
cd ..
python3 generate_datasets.py
cd mpi
```

### Passo 2: Executar Testes

```bash
bash run_tests.sh
```

Este script:
1. Detecta o compilador MPI (mpicc)
2. Compila a versão MPI
3. Verifica se os datasets existem
4. Executa testes com múltiplos processos:
   - Pequeno: 1, 2, 4 processos
   - Médio: 1, 2, 4, 8 processos
   - Grande: 1, 2, 4, 8, 16 processos
5. Salva resultados em assign_mpi*_*.csv e centroids_mpi*_*.csv

## Execução Manual

```bash
mpirun -np 4 ./kmeans_1d_mpi dados_grande.csv centroides_grande.csv 50 0.000001 assign.csv centroids.csv
```

Parâmetros:
1. Arquivo de dados
2. Arquivo de centróides iniciais
3. Número máximo de iterações
4. Epsilon para convergência
5. Arquivo de saída para atribuições (opcional)
6. Arquivo de saída para centróides finais (opcional)

## Arquitetura MPI

### Distribuição de Dados

- **Processo 0 (root):** Lê todos os dados do arquivo
- **Scatterv:** Distribui os N pontos entre P processos
- Cada processo recebe aproximadamente N/P pontos

### Por Iteração

1. **Broadcast:** Todos os processos recebem os centróides C
2. **Assignment Local:** Cada processo calcula:
   - `assign_local[i]` para seus pontos
   - `SSE_local` para seus pontos
3. **Redução Global:**
   - `MPI_Reduce` para somar `SSE_local → SSE_global`
   - `MPI_Allreduce` para somar `sum_local[c]` e `cnt_local[c]`
4. **Update Global:** Todos os processos atualizam C com os resultados globais
5. **Convergência:** Processo 0 verifica e broadcasta o resultado

### Operações MPI Utilizadas

- `MPI_Bcast`: Broadcast dos centróides iniciais e atualizados
- `MPI_Scatterv`: Distribuição balanceada dos pontos
- `MPI_Reduce`: Redução do SSE (apenas processo 0)
- `MPI_Allreduce`: Redução global de sum e cnt (todos os processos)
- `MPI_Gatherv`: Coleta das atribuições finais (apenas processo 0)

## Medições

### Strong Scaling

Teste com P ∈ {1, 2, 4, 8, 16} processos para avaliar:
- Speedup em relação à versão serial
- Speedup em relação à versão OpenMP
- Eficiência paralela
- Tempo de comunicação (overhead de Allreduce)

### Tempo de Comunicação

O custo de comunicação é medido implicitamente:
- `MPI_Allreduce` é a operação mais custosa (2 por iteração)
- Overhead aumenta com número de processos
- Trade-off entre paralelismo e comunicação

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
K-means 1D (MPI)
Processos: 4
N=1000000 K=16 max_iter=50 eps=1e-06
Iterações: 50 | SSE final: 171354.460887 | Tempo: 245.3 ms
```

## Comparação com Outras Versões

### vs Serial
- Distribuição de dados entre processos
- Comunicação adiciona overhead
- Benefício aumenta com N grande

### vs OpenMP
- Memória distribuída vs compartilhada
- Comunicação explícita vs implícita
- Melhor para clusters/distribuição geográfica
- Overhead de comunicação maior

## Troubleshooting

### Erro: "mpicc: command not found"
```bash
# macOS
brew install openmpi

# Linux
sudo apt-get install libopenmpi-dev
```

### Erro: "Dataset não encontrado"
```bash
cd ..
python3 generate_datasets.py
cd mpi
```

### Erro: "Too many processes"
Reduza o número de processos no `run_tests.sh` ou use:
```bash
mpirun -np 4 --oversubscribe ./kmeans_1d_mpi ...
```

### Performance ruim
- Verifique se está usando o dataset correto
- Considere o overhead de comunicação
- Para N pequeno, MPI pode ser mais lento que serial
- Use mais processos apenas para N grande



