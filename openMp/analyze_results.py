#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import re
import os
import sys

def run_tests_and_capture_results():
    print("Executando testes de desempenho...")
    print("=" * 60)
    
    try:
        result = subprocess.run(['bash', 'run_tests.sh'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            print(f"Erro ao executar testes: {result.stderr}")
            return None
            
        print("Testes executados com sucesso!")
        return result.stdout
        
    except Exception as e:
        print(f"Erro: {e}")
        return None

def parse_test_results(output):
    print("Analisando resultados...")
    
    patterns = {
        'iterations': r'Iterações:\s+(\d+)',
        'sse': r'SSE final:\s+([\d.]+)',
        'time': r'Tempo:\s+([\d.]+)\s+ms'
    }
    
    results = {
        'Pequeno (N=10,000)': {'serial': {}, 'omp_1': {}, 'omp_2': {}, 'omp_4': {}, 'omp_8': {}, 'omp_16': {}},
        'Médio (N=100,000)': {'serial': {}, 'omp_1': {}, 'omp_2': {}, 'omp_4': {}, 'omp_8': {}, 'omp_16': {}},
        'Grande (N=1,000,000)': {'serial': {}, 'omp_1': {}, 'omp_2': {}, 'omp_4': {}, 'omp_8': {}, 'omp_16': {}}
    }
    
    section_mapping = {
        'PEQUENO': 'Pequeno (N=10,000)',
        'MÉDIO': 'Médio (N=100,000)', 
        'GRANDE': 'Grande (N=1,000,000)'
    }
    
    config_mapping = {
        'SERIAL': 'serial',
        'OpenMP (1 thread)': 'omp_1',
        'OpenMP (2 threads)': 'omp_2', 
        'OpenMP (4 threads)': 'omp_4',
        'OpenMP (8 threads)': 'omp_8',
        'OpenMP (16 threads)': 'omp_16'
    }
    
    current_dataset = None
    current_config = None
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        
        if 'Testando Dataset' in line:
            for key, dataset in section_mapping.items():
                if key in line:
                    current_dataset = dataset
                    break
        
        elif '---' in line and '---' in line:
            for config_name, config_key in config_mapping.items():
                if config_name in line:
                    current_config = config_key
                    break
        
        elif current_dataset and current_config:
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    value = float(match.group(1))
                    if key not in results[current_dataset][current_config]:
                        results[current_dataset][current_config][key] = value
    
    return results

def create_performance_charts(results):
    print("Gerando gráficos...")
    
    datasets = list(results.keys())
    threads = [1, 2, 4, 8, 16]
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    time_data = {}
    speedup_data = {}
    
    for dataset_name in datasets:
        dataset_results = results[dataset_name]
        serial_time = dataset_results['serial'].get('time', 0)
        
        time_data[dataset_name] = [serial_time]
        speedup_data[dataset_name] = [1.0]
        
        for thread_count in threads:
            config_key = f'omp_{thread_count}'
            if config_key in dataset_results and 'time' in dataset_results[config_key]:
                omp_time = dataset_results[config_key]['time']
                time_data[dataset_name].append(omp_time)
                
                if serial_time > 0:
                    speedup = serial_time / omp_time
                    speedup_data[dataset_name].append(speedup)
                else:
                    speedup_data[dataset_name].append(1.0)
            else:
                time_data[dataset_name].append(serial_time)
                speedup_data[dataset_name].append(1.0)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    for i, dataset_name in enumerate(datasets):
        times = time_data[dataset_name]
        omp_times = times[1:]
        ax1.plot(threads, omp_times, marker='o', linewidth=2, markersize=8, 
                label=dataset_name, color=colors[i])
        ax1.axhline(y=times[0], color=colors[i], linestyle='--', alpha=0.5)

    ax1.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Tempo de Execução (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Tempo de Execução vs. Número de Threads', fontsize=14, fontweight='bold')
    ax1.set_xticks(threads)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    all_times = []
    for times in time_data.values():
        all_times.extend(times[1:])
    if any(t > 0 for t in all_times):
        ax1.set_yscale('log')
    
    for i, dataset_name in enumerate(datasets):
        speedups = speedup_data[dataset_name]
        omp_speedups = speedups[1:]
        ax2.plot(threads, omp_speedups, marker='s', linewidth=2, markersize=8,
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
    
    return time_data, speedup_data

def print_analysis_report(results, time_data, speedup_data):
    print("\n" + "="*60)
    print("ANÁLISE DE DESEMPENHO - K-MEANS COM OPENMP")
    print("="*60)
    
    datasets = list(results.keys())
    threads = [1, 2, 4, 8, 16]
    
    for dataset_name in datasets:
        print(f"\n {dataset_name}")
        print("-" * 60)
        
        dataset_results = results[dataset_name]
        
        serial_time = dataset_results['serial'].get('time', 0)
        serial_sse = dataset_results['serial'].get('sse', 0)
        serial_iter = dataset_results['serial'].get('iterations', 0)
        print(f"  Serial:        {serial_time:8.1f} ms (SSE: {serial_sse:.2f}, Iter: {serial_iter})")
        
        for i, thread_count in enumerate(threads):
            config_key = f'omp_{thread_count}'
            if config_key in dataset_results:
                omp_time = dataset_results[config_key].get('time', 0)
                omp_sse = dataset_results[config_key].get('sse', 0)
                omp_iter = dataset_results[config_key].get('iterations', 0)
                speedup = speedup_data[dataset_name][i+1]
                print(f"  OpenMP ({thread_count:2d}t): {omp_time:8.1f} ms (SSE: {omp_sse:.2f}, Iter: {omp_iter}, Speedup: {speedup:.2f}x)")
        
        best_speedup = max(speedup_data[dataset_name][1:])
        best_thread_idx = speedup_data[dataset_name][1:].index(best_speedup) + 1
        best_threads = threads[best_thread_idx - 1]
        print(f"\n  Melhor configuração: {best_threads} threads com speedup de {best_speedup:.2f}x")
    
    print("\n" + "="*60)
    print("💡 OBSERVAÇÕES")
    print("="*60)
    print("""
1. Validação de corretude: SSE deve ser idêntico entre versões
2. Speedup > 1.0 indica melhoria de desempenho
3. Para datasets pequenos, overhead pode prejudicar performance
4. Para datasets grandes, paralelização é mais eficaz
5. 4 threads geralmente oferece melhor custo-benefício
""")

def main():
    print("🎯 K-means OpenMP - Análise Automática de Desempenho")
    print("=" * 60)
    
    if not os.path.exists('run_tests.sh'):
        print("Erro: Script run_tests.sh não encontrado!")
        print("Certifique-se de estar na pasta openMp/")
        sys.exit(1)
    
    test_output = run_tests_and_capture_results()
    if not test_output:
        print("Falha ao executar testes!")
        sys.exit(1)
    
    results = parse_test_results(test_output)
    if not results:
        print("Falha ao analisar resultados!")
        sys.exit(1)
    
    time_data, speedup_data = create_performance_charts(results)
    print_analysis_report(results, time_data, speedup_data)
    
    print("\nAnálise concluída com sucesso!")
    print("Arquivos gerados:")
    print("   - performance_analysis.png (gráficos)")
    print("   - assign_*.csv (resultados de clustering)")
    print("   - centroids_*.csv (centróides finais)")

if __name__ == "__main__":
    main()
