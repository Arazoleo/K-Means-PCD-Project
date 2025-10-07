# Relatório de Desempenho: K-means 1D com OpenMP

## Resumo Executivo

Este relatório apresenta os resultados da implementação e análise de desempenho do algoritmo K-means 1D paralelizado com OpenMP. Os testes foram realizados com três tamanhos de datasets diferentes, comparando a versão sequencial (baseline) com a versão paralela utilizando 1, 2, 4 e 8 threads.

## Ambiente de Testes

**Sistema Operacional:** Ubuntu 22.04 LTS  
**Compilador:** GCC 11.4.0  
**Flags de Compilação:**
- Versão Serial: `gcc -O2 -std=c99 kmeans_1d_serial.c -o kmeans_1d_serial -lm`
- Versão OpenMP: `gcc -O2 -fopenmp -std=c99 kmeans_1d_omp.c -o kmeans_1d_omp -lm`

**Medição de Tempo:**
- Versão Serial: `clock()` (tempo de CPU)
- Versão OpenMP: `omp_get_wtime()` (tempo de parede/wall time)

## Datasets de Teste

Foram gerados três conjuntos de dados sintéticos com clusters bem definidos:

| Dataset | Número de Pontos (N) | Número de Clusters (K) | Iterações até Convergência |
|---------|---------------------|------------------------|---------------------------|
| Pequeno | 10.000              | 4                      | 3                         |
| Médio   | 100.000             | 8                      | 5                         |
| Grande  | 1.000.000           | 16                     | 31                        |

## Resultados de Desempenho

### Dataset Pequeno (N=10.000, K=4)

| Configuração | Tempo (ms) | Speedup |
|--------------|-----------|---------|
| Serial       | 0.1       | 1.00x   |
| OpenMP (1t)  | 0.1       | 1.00x   |
| OpenMP (2t)  | 0.2       | 0.50x   |
| OpenMP (4t)  | 0.4       | 0.25x   |
| OpenMP (8t)  | 2.6       | 0.04x   |

**Análise:** Para datasets pequenos, o overhead da criação e sincronização de threads supera qualquer ganho de desempenho. A versão serial é mais eficiente.

### Dataset Médio (N=100.000, K=8)

| Configuração | Tempo (ms) | Speedup |
|--------------|-----------|---------|
| Serial       | 3.7       | 1.00x   |
| OpenMP (1t)  | 4.0       | 0.93x   |
| OpenMP (2t)  | 2.3       | 1.61x   |
| OpenMP (4t)  | 1.6       | **2.31x**   |
| OpenMP (8t)  | 5.0       | 0.74x   |

**Análise:** Começamos a observar ganhos significativos com 2 e 4 threads. A melhor configuração é **4 threads com speedup de 2.31x**. Com 8 threads, o overhead volta a prejudicar o desempenho.

### Dataset Grande (N=1.000.000, K=16)

| Configuração | Tempo (ms) | Speedup |
|--------------|-----------|---------|
| Serial       | 446.8     | 1.00x   |
| OpenMP (1t)  | 430.2     | 1.04x   |
| OpenMP (2t)  | 219.5     | 2.04x   |
| OpenMP (4t)  | 113.7     | **3.93x**   |
| OpenMP (8t)  | 135.0     | 3.31x   |

**Análise:** Com datasets grandes, os ganhos de desempenho são substanciais. A melhor configuração é **4 threads com speedup de 3.93x**, reduzindo o tempo de execução de 446.8ms para 113.7ms. O desempenho com 8 threads é ligeiramente inferior a 4 threads, provavelmente devido à limitação de núcleos físicos disponíveis.

## Visualização dos Resultados

![Análise de Desempenho](performance_analysis.png)

O gráfico à esquerda mostra o tempo de execução em escala logarítmica, evidenciando como o tempo diminui com mais threads apenas para datasets maiores. O gráfico à direita mostra o speedup em relação à linha ideal (speedup linear), demonstrando que o melhor resultado foi obtido com 4 threads no dataset grande, alcançando quase 4x de aceleração.

## Discussão

### Fatores que Limitam o Speedup

O speedup observado não atinge o ideal linear devido a diversos fatores:

**Overhead de Paralelização:** A criação, gerenciamento e sincronização de threads introduz um custo fixo que é mais significativo em datasets pequenos.

**Seções Críticas:** A função `update_step_1d` utiliza uma seção crítica (`#pragma omp critical`) para combinar os acumuladores de cada thread, o que serializa parte do código e limita o paralelismo.

**Limitações de Hardware:** O ambiente de testes pode ter limitação no número de núcleos físicos. Com 8 threads, é possível que estejamos utilizando núcleos lógicos (hyperthreading), o que não oferece o mesmo ganho de desempenho que núcleos físicos.

**Contenção de Memória e Cache:** Com múltiplas threads acessando a mesma estrutura de dados, pode haver contenção no acesso à memória e invalidação de cache, reduzindo a eficiência.

### Recomendações

Com base nos resultados obtidos, recomendamos:

**Para datasets pequenos (N < 50.000):** Utilize a versão sequencial, pois o overhead da paralelização não compensa.

**Para datasets médios (50.000 < N < 500.000):** Utilize 2 a 4 threads para obter ganhos moderados de desempenho.

**Para datasets grandes (N > 500.000):** Utilize 4 threads para obter o melhor speedup. Mais threads podem não trazer benefícios adicionais dependendo do hardware disponível.

## Validação da Corretude

Todos os testes produziram o mesmo valor de SSE (Sum of Squared Errors) final, independentemente do número de threads utilizado, confirmando que a implementação paralela está correta e produz resultados idênticos à versão serial:

- Dataset Pequeno: SSE = 40.248,10
- Dataset Médio: SSE = 399.263,02
- Dataset Grande: SSE = 2.678.304,07

## Conclusão

A paralelização do algoritmo K-means 1D com OpenMP demonstrou ser eficaz para datasets grandes, alcançando um speedup de até **3.93x com 4 threads**. No entanto, é fundamental considerar o tamanho do dataset ao decidir utilizar paralelização, pois o overhead pode ser contraproducente para datasets pequenos.

Os resultados obtidos estão alinhados com a teoria de computação paralela, onde o ganho de desempenho é proporcional ao tamanho do problema e limitado por fatores como overhead de sincronização, seções críticas e limitações de hardware.

## Próximos Passos

Para melhorar ainda mais o desempenho, as seguintes otimizações podem ser consideradas:

1. **Reduzir seções críticas:** Utilizar operações atômicas ou técnicas de redução mais eficientes na função `update_step_1d`.
2. **Ajustar o scheduling:** Testar diferentes políticas de escalonamento (`static`, `dynamic`, `guided`) e tamanhos de chunk.
3. **Implementar versões CUDA e MPI:** Conforme proposto no projeto, para explorar paralelismo em GPU e ambientes distribuídos.
4. **Otimizar localidade de dados:** Reorganizar estruturas de dados para melhorar o uso de cache.

## Arquivos Gerados

- `kmeans_1d_serial.c` - Código fonte da versão sequencial
- `kmeans_1d_omp.c` - Código fonte da versão OpenMP
- `generate_datasets.py` - Script para geração de datasets
- `run_tests.sh` - Script automatizado de testes
- `analyze_results.py` - Script de análise e visualização
- `performance_analysis.png` - Gráficos de desempenho
- `test_results_fixed.txt` - Log completo dos testes
- Datasets: `dados_pequeno.csv`, `dados_medio.csv`, `dados_grande.csv`
- Centróides: `centroides_pequeno.csv`, `centroides_medio.csv`, `centroides_grande.csv`
