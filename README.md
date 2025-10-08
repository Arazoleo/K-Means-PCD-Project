# K-means 1D com OpenMP - Guia de Compilação e Execução

## 🚀 Compilação Rápida


### Compilação
```bash
# Navegue para a pasta do projeto
cd /Users/arazoleonardo/Downloads/kmeans_openmp_results/openMp

# Compilar versão serial
/opt/homebrew/bin/gcc-15 -O2 -std=c99 method_means_1d_serial.c -o kmeans_1d_serial -lm

# Compilar versão OpenMP
/opt/homebrew/bin/gcc-15 -O2 -fopenmp -std=c99 method_means_1d_omp.c -o kmeans_1d_omp -lm
```

## 📊 Execução dos Testes

### Teste Automatizado Completo
```bash
# Executa todos os testes (serial + OpenMP com 1,2,4,8,16 threads)
bash run_tests.sh
```

### Teste Manual Individual
```bash
# Teste serial
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_serial.csv centroids_serial.csv

# Teste OpenMP (4 threads)
export OMP_NUM_THREADS=4
./kmeans_1d_omp dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign_omp4.csv centroids_omp4.csv
```

## 📁 Arquivos de Saída

Cada execução gera **2 arquivos obrigatórios**:

### 1. `assign_[versao]_[dataset].csv`
- **N linhas** (uma por ponto)
- **Conteúdo**: Índice do cluster (0, 1, 2, ..., K-1)
- **Exemplo**: 
```
0
1
0
2
1
```

### 2. `centroids_[versao]_[dataset].csv`
- **K linhas** (uma por cluster)
- **Conteúdo**: Coordenada final do centróide
- **Exemplo**:
```
15.234567
25.123456
35.456789
45.789012
```

## 🔍 Como Conferir os Resultados

### 1. Verificar Saída no Terminal
Cada execução mostra:
```
Iterações: 5
SSE final: 399.263
Tempo total: 1.6 ms
```

### 2. Validar Arquivos de Saída
```bash
# Verificar número de linhas (deve ser igual ao número de pontos)
wc -l assign_serial_pequeno.csv
# Saída esperada: 10000 assign_serial_pequeno.csv

# Verificar centróides finais
cat centroids_serial_pequeno.csv
```

### 3. Comparar Resultados Entre Versões
```bash
# Verificar se SSE é igual entre versões (validação de corretude)
grep "SSE final" test_results_fixed.txt

# Comparar centróides finais (devem ser idênticos)
diff centroids_serial_pequeno.csv centroids_omp4_pequeno.csv
```

## 📈 Análise de Desempenho

### Gerar Gráficos
```bash
python3 analyze_results.py
```
**Saída**: `performance_analysis.png` com gráficos de tempo e speedup

### Interpretar Resultados
- **Speedup > 1.0**: Versão paralela é mais rápida
- **Speedup < 1.0**: Overhead da paralelização prejudica desempenho
- **SSE idêntico**: Validação de que resultados são corretos

## 🎯 Resultados Esperados

| Dataset | Melhor Configuração | Speedup Esperado |
|---------|-------------------|------------------|
| Pequeno (N=10K) | Serial | 1.00x |
| Médio (N=100K) | 4 threads | ~2.3x |
| Grande (N=1M) | 4 threads | ~3.9x |

## 🛠️ Solução de Problemas

### Erro: "unsupported option '-fopenmp'"
```bash
# Use o GCC do Homebrew em vez do Clang padrão
/opt/homebrew/bin/gcc-15 --version
```

### Erro: "No such file or directory"
```bash
# Certifique-se de estar na pasta correta
cd /Users/arazoleonardo/Downloads/kmeans_openmp_results/openMp
ls -la *.csv *.c
```

### Arquivos de saída não gerados
```bash
# Verifique se os parâmetros estão corretos
./kmeans_1d_serial dados_pequeno.csv centroides_pequeno.csv 50 0.000001 assign.csv centroids.csv
```

## 📋 Checklist de Validação

- [ ] Compilação sem erros
- [ ] Execução completa do `run_tests.sh`
- [ ] Arquivos `assign_*.csv` gerados (N linhas cada)
- [ ] Arquivos `centroids_*.csv` gerados (K linhas cada)
- [ ] SSE idêntico entre versões serial e paralela
- [ ] Speedup > 1.0 para datasets grandes
- [ ] Gráfico `performance_analysis.png` gerado

## 📁 Estrutura de Arquivos

```
openMp/
├── method_means_1d_serial.c    # Código serial
├── method_means_1d_omp.c       # Código OpenMP
├── run_tests.sh                # Script de testes
├── generate_datasets.py        # Gerador de dados
├── analyze_results.py          # Análise e gráficos
├── dados_*.csv                 # Datasets de entrada
├── centroides_*.csv            # Centróides iniciais
├── assign_*.csv                # Resultados: cluster por ponto
├── centroids_*.csv             # Resultados: centróides finais
└── performance_analysis.png    # Gráficos de desempenho
```
