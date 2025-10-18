#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.5)
plt.rcParams['figure.figsize'] = (12, 8)

threads = np.array([1, 2, 4, 8, 16])

tempo_pequeno = np.array([4.8, 1.4, 1.8, 2.6, 3.5])
tempo_medio = np.array([105.4, 52.3, 40.6, 30.5, 35.6])
tempo_grande = np.array([1279.1, 677.2, 389.1, 269.1, 289.3])
tempo_serial_pequeno = 1.6
tempo_serial_medio = 96.2
tempo_serial_grande = 1265.2

speedup_pequeno = tempo_serial_pequeno / tempo_pequeno
speedup_medio = tempo_serial_medio / tempo_medio
speedup_grande = tempo_serial_grande / tempo_grande

cores = ['#2E86AB', '#A23B72', '#F18F01']


plt.figure(figsize=(12, 8))
plt.plot(threads, tempo_pequeno, marker='o', linewidth=3, markersize=10, 
         label='Pequeno (N=10K)', color=cores[0])
plt.plot(threads, tempo_medio, marker='s', linewidth=3, markersize=10, 
         label='Médio (N=100K)', color=cores[1])
plt.plot(threads, tempo_grande, marker='^', linewidth=3, markersize=10, 
         label='Grande (N=1M)', color=cores[2])

plt.axhline(y=tempo_serial_pequeno, color=cores[0], linestyle='--', linewidth=2, alpha=0.5)
plt.axhline(y=tempo_serial_medio, color=cores[1], linestyle='--', linewidth=2, alpha=0.5)
plt.axhline(y=tempo_serial_grande, color=cores[2], linestyle='--', linewidth=2, alpha=0.5)

plt.xlabel('Número de Threads', fontweight='bold', fontsize=16)
plt.ylabel('Tempo de Execução (ms)', fontweight='bold', fontsize=16)
plt.title('Tempo de Execução vs. Número de Threads', fontweight='bold', fontsize=18, pad=20)
plt.xticks(threads)
plt.legend(fontsize=14, loc='best', frameon=True, shadow=True)
plt.grid(True, alpha=0.3, linestyle='--')
plt.yscale('log')
plt.tight_layout()
plt.savefig('grafico_tempo.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico 1 salvo: grafico_tempo.png")
plt.close()

plt.figure(figsize=(12, 8))
plt.plot(threads, speedup_pequeno, marker='o', linewidth=3, markersize=10, 
         label='Pequeno (N=10K)', color=cores[0])
plt.plot(threads, speedup_medio, marker='s', linewidth=3, markersize=10, 
         label='Médio (N=100K)', color=cores[1])
plt.plot(threads, speedup_grande, marker='^', linewidth=3, markersize=10, 
         label='Grande (N=1M)', color=cores[2])
plt.plot(threads, threads, 'k--', linewidth=3, label='Speedup Ideal (Linear)', alpha=0.6)

for i, txt in enumerate(speedup_grande):
    if i in [2, 3]:
        plt.annotate(f'{txt:.2f}x', (threads[i], speedup_grande[i]), 
                    textcoords="offset points", xytext=(0,10), ha='center', 
                    fontsize=11, fontweight='bold')

plt.xlabel('Número de Threads', fontweight='bold', fontsize=16)
plt.ylabel('Speedup', fontweight='bold', fontsize=16)
plt.title('Speedup vs. Número de Threads', fontweight='bold', fontsize=18, pad=20)
plt.xticks(threads)
plt.legend(fontsize=14, loc='best', frameon=True, shadow=True)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('grafico_speedup.png', dpi=300, bbox_inches='tight')
print("Gráfico 2 salvo: grafico_speedup.png")
plt.close()

print("\nTodos os gráficos foram gerados com sucesso!")

