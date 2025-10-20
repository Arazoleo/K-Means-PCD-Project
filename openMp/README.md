# K-Means 1D - Versão OpenMP

Implementação paralela do algoritmo K-means unidimensional usando OpenMP, incluindo testes de diferentes políticas de escalonamento (schedule) e tamanhos de chunk.

## Requisitos

- GCC com suporte a OpenMP
- Python 3 com numpy, matplotlib e seaborn

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

### Versão com Schedule Runtime

Para testes de diferentes políticas de escalonamento:

```bash
gcc-15 -O2 -fopenmp -std=c99 method_means_1d_omp_schedule.c -o kmeans_schedule -lm
```

## Como Executar

### Passo 1: Gerar Datasets

Na raiz do projeto:

```bash
cd ..
python3 generate_datasets.py
cd openmp
```

### Passo 2: Executar Testes Padrão

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

### Passo 3: Testes de Schedule e Chunk Size

```bash
bash test_schedule.sh
```

Testa automaticamente no dataset grande (N=1M, K=16):
- Threads: 1, 2, 4, 8, 16
- Schedules: static(1000, 10000), dynamic(1000), guided

### Passo 4: Analisar Resultados

```bash
python3 analyze_results.py
python3 analise_schedule.py
```

Gera:
- performance_analysis_openmp.png
- Gráficos de tempo e speedup
- Análise detalhada de schedule
- Relatório comparativo no terminal

## Execução Manual

### Versão Padrão

```bash
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign.csv centroids.csv
```

### Versão com Schedule

```bash
export OMP_NUM_THREADS=8
export OMP_SCHEDULE="dynamic,1000"
./kmeans_schedule dados_grande.csv centroides_grande.csv 50 0.000001
```

Parâmetros:
1. Arquivo de dados
2. Arquivo de centróides iniciais
3. Número máximo de iterações
4. Epsilon para convergência
5. Arquivo de saída para atribuições (opcional)
6. Arquivo de saída para centróides finais (opcional)

Controle o número de threads via variável OMP_NUM_THREADS.

## Políticas de Escalonamento (Schedule)

Schedule define como as iterações do loop paralelo são distribuídas entre as threads:

### static
Divide as iterações em blocos de tamanho fixo antes da execução.
- Baixo overhead
- Boa para cargas balanceadas
- Chunk size define o tamanho do bloco por thread

### dynamic
Distribui iterações dinamicamente durante a execução.
- Maior overhead
- Melhor para cargas desbalanceadas
- Chunk size define quantas iterações são atribuídas por vez

### guided
Similar ao dynamic, mas o chunk size diminui gradualmente.
- Overhead médio
- Adaptativo
- Chunk size define o tamanho mínimo

### Configurações Disponíveis

```bash
export OMP_SCHEDULE="static"           # Padrão do compilador
export OMP_SCHEDULE="static,1000"      # Chunk fixo de 1000
export OMP_SCHEDULE="dynamic"          # Padrão do compilador
export OMP_SCHEDULE="dynamic,1000"     # Chunk fixo de 1000
export OMP_SCHEDULE="guided"           # Padrão do compilador
export OMP_SCHEDULE="guided,100"       # Chunk mínimo de 100
```

## Paralelização

### Assignment Step
```c
#pragma omp parallel for reduction(+:sse)
```
Cada thread processa um subconjunto dos N pontos.

### Update Step
Acumuladores locais por thread com redução em região crítica.

## Resultados de Schedule

Dataset: GRANDE (N=1M, K=16)

### Tabela de Tempos (ms)

| Threads | static,1000 | static,10000 | dynamic,1000 | guided |
|---------|-------------|--------------|--------------|--------|
| 1       | 1351.2      | 1337.7       | 1312.5       | 1299.4 |
| 2       | 693.3       | 667.1        | 685.1        | 697.3  |
| 4       | 392.5       | 381.6        | 361.3        | 368.0  |
| 8       | 312.9       | 501.2        | **246.1**    | 267.3  |
| 16      | 283.6       | 299.2        | 250.1        | 265.4  |

### Melhor Configuração por Threads

| Threads | Melhor Schedule | Tempo (ms) | Speedup |
|---------|----------------|------------|---------|
| 1       | guided         | 1299.4     | 1.00x   |
| 2       | static,10000   | 667.1      | 1.95x   |
| 4       | dynamic,1000   | 361.3      | 3.60x   |
| 8       | **dynamic,1000**| **246.1**  | **5.28x** |
| 16      | dynamic,1000   | 250.1      | 5.20x   |

### Conclusões dos Testes

1. **Melhor desempenho absoluto**: 8 threads com `dynamic,1000` (246.1 ms)
2. **Melhor speedup**: 8 threads com `dynamic,1000` (5.28x)
3. **Observações**:
   - `dynamic,1000` é consistentemente melhor com 4+ threads
   - `static` com chunks grandes degrada com muitas threads
   - `guided` oferece bom compromisso em todas as configurações
   - Eficiência diminui com 16 threads (overhead)

4. **Recomendação para N=1M, K=16**:
   - Primeira opção: 8 threads com `dynamic,1000`
   - Alternativa: 8 threads com `guided`

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

### Versão Padrão
```
K-means 1D (OpenMP)
Threads: 4
N=10000 K=4 max_iter=50 eps=1e-06
Iterações: 12 | SSE final: 61203.756968 | Tempo: 1.8 ms
```

### Versão com Schedule
```
K-means 1D (OpenMP Schedule)
Threads: 8 | Schedule: dynamic,1000
N=1000000 K=16 max_iter=50 eps=1e-06
Iterações: 50 | SSE final: 171354.460887 | Tempo: 246.1 ms
```

## Arquivos do Projeto

### Implementação Principal
- `method_means_1d_omp.c`: Versão OpenMP padrão
- `run_tests.sh`: Script de testes padrão
- `analyze_results.py`: Análise de resultados padrão

### Testes de Schedule
- `method_means_1d_omp_schedule.c`: Versão com schedule(runtime)
- `test_schedule.sh`: Script de testes de schedule
- `analise_schedule.py`: Análise detalhada de schedule
- `README_SCHEDULE.md`: Documentação específica (agora integrada aqui)

## Troubleshooting

### Erro: "unsupported option '-fopenmp'"
```bash
# macOS
brew install gcc
# Use gcc-15 em vez de gcc

# Linux
sudo apt-get install gcc
```

### Erro: "Dataset não encontrado"
```bash
cd ..
python3 generate_datasets.py
cd openmp
```

### Performance ruim
- Verifique se está usando o dataset correto
- Teste diferentes configurações de schedule
- Considere o overhead do sistema operacional