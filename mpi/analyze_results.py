#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import re
import os

def parse_test_results():
    print("Analisando resultados dos testes MPI...")
    print("=" * 60)
    
    results = {
        'Pequeno (N=10,000, K=4)': {},
        'Médio (N=100,000, K=8)': {},
        'Grande (N=1,000,000, K=16)': {}
    }
    
    try:
        result = subprocess.run(['bash', 'run_tests.sh'], 
                              capture_output=True, text=True, cwd='.')
        
        output = result.stdout + result.stderr
        
        current_dataset = None
        current_processes = None
        
        for line in output.split('\n'):
            if 'Dataset PEQUENO' in line:
                current_dataset = 'Pequeno (N=10,000, K=4)'
            elif 'Dataset MÉDIO' in line:
                current_dataset = 'Médio (N=100,000, K=8)'
            elif 'Dataset GRANDE' in line:
                current_dataset = 'Grande (N=1,000,000, K=16)'
            elif 'MPI com' in line:
                match = re.search(r'(\d+)\s+processo', line)
                if match:
                    current_processes = int(match.group(1))
            elif 'Tempo:' in line and current_dataset and current_processes:
                match = re.search(r'Tempo:\s+([\d.]+)\s+ms', line)
                if match:
                    time = float(match.group(1))
                    key = f'mpi_{current_processes}'
                    if key not in results[current_dataset]:
                        results[current_dataset][key] = {}
                    results[current_dataset][key]['time'] = time
                    
                    sse_match = re.search(r'SSE final:\s+([\d.]+)', line)
                    if sse_match:
                        results[current_dataset][key]['sse'] = float(sse_match.group(1))
                    
                    iter_match = re.search(r'Iterações:\s+(\d+)', line)
                    if iter_match:
                        results[current_dataset][key]['iterations'] = int(iter_match.group(1))
        
        return results
        
    except Exception as e:
        print(f"Erro ao analisar: {e}")
        return None

def calculate_speedup(results, serial_times):
    speedups = {}
    for dataset, configs in results.items():
        speedups[dataset] = {}
        serial_time = serial_times.get(dataset, 0)
        if serial_time == 0:
            continue
        for config, data in configs.items():
            if 'time' in data:
                speedups[dataset][config] = serial_time / data['time']
    return speedups

def plot_results(results, speedups):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    datasets = ['Pequeno (N=10,000, K=4)', 'Médio (N=100,000, K=8)', 'Grande (N=1,000,000, K=16)']
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    for idx, dataset in enumerate(datasets):
        if dataset not in results:
            continue
            
        configs = results[dataset]
        processes = []
        times = []
        spds = []
        
        for config in sorted(configs.keys(), key=lambda x: int(x.split('_')[1])):
            p = int(config.split('_')[1])
            processes.append(p)
            times.append(configs[config]['time'])
            if dataset in speedups and config in speedups[dataset]:
                spds.append(speedups[dataset][config])
            else:
                spds.append(0)
        
        ax1 = axes[idx // 2, idx % 2]
        ax1.plot(processes, times, marker='o', linewidth=2, markersize=8, 
                label='Tempo (ms)', color=colors[idx])
        ax1.set_xlabel('Número de Processos')
        ax1.set_ylabel('Tempo (ms)')
        ax1.set_title(f'{dataset}')
        ax1.set_xticks(processes)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        if idx == 0:
            ax2 = axes[1, 1]
            ax2.plot(processes, spds, marker='s', linewidth=2, markersize=8,
                    label=dataset, color=colors[idx])
    
    ax2 = axes[1, 1]
    ax2.set_xlabel('Número de Processos')
    ax2.set_ylabel('Speedup')
    ax2.set_title('Speedup vs Processos')
    ax2.set_xticks(processes)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('performance_analysis_mpi.png', dpi=300, bbox_inches='tight')
    print("Gráfico salvo: performance_analysis_mpi.png")
    plt.close()

def print_summary(results, speedups):
    print("\n" + "=" * 60)
    print("RESUMO DOS RESULTADOS MPI")
    print("=" * 60)
    
    serial_times = {
        'Pequeno (N=10,000, K=4)': 1.6,
        'Médio (N=100,000, K=8)': 96.2,
        'Grande (N=1,000,000, K=16)': 1265.2
    }
    
    for dataset in ['Pequeno (N=10,000, K=4)', 'Médio (N=100,000, K=8)', 'Grande (N=1,000,000, K=16)']:
        if dataset not in results:
            continue
            
        print(f"\n{dataset}:")
        print("-" * 60)
        print(f"{'Processos':<12} {'Tempo (ms)':<15} {'Speedup':<12} {'SSE':<15}")
        print("-" * 60)
        
        serial_time = serial_times.get(dataset, 0)
        print(f"{'Serial':<12} {serial_time:<15.1f} {'1.00x':<12} {'---':<15}")
        
        for config in sorted(results[dataset].keys(), key=lambda x: int(x.split('_')[1])):
            p = int(config.split('_')[1])
            data = results[dataset][config]
            time = data.get('time', 0)
            sse = data.get('sse', 0)
            spd = speedups.get(dataset, {}).get(config, 0)
            
            print(f"{p:<12} {time:<15.1f} {spd:<12.2f} {sse:<15.6f}")

def main():
    results = parse_test_results()
    
    if not results:
        print("Nenhum resultado encontrado. Execute run_tests.sh primeiro.")
        return
    
    serial_times = {
        'Pequeno (N=10,000, K=4)': 1.6,
        'Médio (N=100,000, K=8)': 96.2,
        'Grande (N=1,000,000, K=16)': 1265.2
    }
    
    speedups = calculate_speedup(results, serial_times)
    
    print_summary(results, speedups)
    plot_results(results, speedups)
    
    print("\nAnálise concluída!")

if __name__ == '__main__':
    main()



