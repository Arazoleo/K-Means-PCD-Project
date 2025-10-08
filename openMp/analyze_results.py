#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

datasets = {
    'Pequeno (N=10,000)': {
        'serial': 0.1,
        'omp_1': 0.1,
        'omp_2': 0.2,
        'omp_4': 0.4,
        'omp_8': 2.6,
        'omp_16': 4.2,
    },
    'Médio (N=100,000)': {
        'serial': 3.7,
        'omp_1': 4.0,
        'omp_2': 2.3,
        'omp_4': 1.6,
        'omp_8': 5.0,
        'omp_16': 8.5,
    },
    'Grande (N=1,000,000)': {
        'serial': 446.8,
        'omp_1': 430.2,
        'omp_2': 219.5,
        'omp_4': 113.7,
        'omp_8': 135.0,
        'omp_16': 180.3,
    }
}

speedups = {}
for dataset_name, times in datasets.items():
    serial_time = times['serial']
    speedups[dataset_name] = {
        '1': serial_time / times['omp_1'],
        '2': serial_time / times['omp_2'],
        '4': serial_time / times['omp_4'],
        '8': serial_time / times['omp_8'],
        '16': serial_time / times['omp_16'],
    }

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

threads = [1, 2, 4, 8, 16]
colors = ['#2E86AB', '#A23B72', '#F18F01']

for i, (dataset_name, times) in enumerate(datasets.items()):
    omp_times = [times['omp_1'], times['omp_2'], times['omp_4'], times['omp_8'], times['omp_16']]
    ax1.plot(threads, omp_times, marker='o', linewidth=2, markersize=8, 
             label=dataset_name, color=colors[i])
    ax1.axhline(y=times['serial'], color=colors[i], linestyle='--', alpha=0.5)

ax1.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tempo de Execução (ms)', fontsize=12, fontweight='bold')
ax1.set_title('Tempo de Execução vs. Número de Threads', fontsize=14, fontweight='bold')
ax1.set_xticks(threads)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_yscale('log')

for i, (dataset_name, sp) in enumerate(speedups.items()):
    speedup_values = [sp['1'], sp['2'], sp['4'], sp['8'], sp['16']]
    ax2.plot(threads, speedup_values, marker='s', linewidth=2, markersize=8,
             label=dataset_name, color=colors[i])

ax2.plot(threads, threads, 'k--', linewidth=2, label='Speedup Ideal (Linear)', alpha=0.5)

ax2.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
ax2.set_ylabel('Speedup', fontsize=12, fontweight='bold')
ax2.set_title('Speedup vs. Número de Threads', fontsize=14, fontweight='bold')
ax2.set_xticks(threads)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('performance_analysis.png', dpi=300, bbox_inches='tight')
print("Gráfico salvo: performance_analysis.png")

print("\n" + "="*60)
print("ANÁLISE DE DESEMPENHO - K-MEANS COM OPENMP")
print("="*60)

for dataset_name, times in datasets.items():
    print(f"\n{dataset_name}")
    print("-" * 60)
    print(f"  Tempo Serial:        {times['serial']:8.1f} ms")
    print(f"  Tempo OpenMP (1t):   {times['omp_1']:8.1f} ms (speedup: {speedups[dataset_name]['1']:.2f}x)")
    print(f"  Tempo OpenMP (2t):   {times['omp_2']:8.1f} ms (speedup: {speedups[dataset_name]['2']:.2f}x)")
    print(f"  Tempo OpenMP (4t):   {times['omp_4']:8.1f} ms (speedup: {speedups[dataset_name]['4']:.2f}x)")
    print(f"  Tempo OpenMP (8t):   {times['omp_8']:8.1f} ms (speedup: {speedups[dataset_name]['8']:.2f}x)")
    print(f"  Tempo OpenMP (16t):  {times['omp_16']:8.1f} ms (speedup: {speedups[dataset_name]['16']:.2f}x)")
    
    best_threads = max(speedups[dataset_name], key=speedups[dataset_name].get)
    best_speedup = speedups[dataset_name][best_threads]
    print(f"\n  Melhor configuração: {best_threads} threads com speedup de {best_speedup:.2f}x")

print("\n" + "="*60)
print("OBSERVAÇÕES")
print("="*60)
print("""
1. Para datasets pequenos (N=10,000), o overhead da paralelização
   supera os ganhos, resultando em desempenho pior com mais threads.

2. Para datasets médios (N=100,000), começamos a ver ganhos com 2-4 threads,
   mas 8 threads já apresenta overhead excessivo.

3. Para datasets grandes (N=1,000,000), o ganho é significativo:
   - 2 threads: speedup de ~2x
   - 4 threads: speedup de ~4x (melhor resultado)
   - 8 threads: speedup diminui devido ao overhead e possível limitação
     de núcleos físicos disponíveis.

4. O speedup ideal (linear) não é alcançado devido a:
   - Overhead de criação e sincronização de threads
   - Seções críticas no código (update step)
   - Limitações de memória e cache
   - Possível limitação de núcleos físicos vs. lógicos
""")
