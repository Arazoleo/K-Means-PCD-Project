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
        'Pequeno (N=10,000, K=4)': {},
        'Médio (N=100,000, K=8)': {},
        'Grande (N=1,000,000, K=16)': {}
    }
    
    section_mapping = {
        'PEQUENO': 'Pequeno (N=10,000, K=4)',
        'MÉDIO': 'Médio (N=100,000, K=8)', 
        'GRANDE': 'Grande (N=1,000,000, K=16)'
    }
    
    current_dataset = None
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        
        if 'Testando Dataset' in line:
            for key, dataset in section_mapping.items():
                if key in line:
                    current_dataset = dataset
                    break
        
        elif current_dataset:
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    value = float(match.group(1))
                    if key not in results[current_dataset]:
                        results[current_dataset][key] = value
    
    return results

def create_performance_charts(results):
    print("Gerando gráficos...")
    
    datasets = list(results.keys())
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    times = []
    sses = []
    iters = []
    
    for dataset_name in datasets:
        dataset_results = results[dataset_name]
        times.append(dataset_results.get('time', 0))
        sses.append(dataset_results.get('sse', 0))
        iters.append(dataset_results.get('iterations', 0))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    dataset_labels = ['Pequeno\n(10K)', 'Médio\n(100K)', 'Grande\n(1M)']
    x_pos = np.arange(len(dataset_labels))
    
    bars = ax1.bar(x_pos, times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Dataset', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Tempo de Execução (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Tempo de Execução - Versão Serial', fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(dataset_labels)
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.1f} ms',
                ha='center', va='bottom', fontweight='bold')
    
    bars2 = ax2.bar(x_pos, iters, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Dataset', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Número de Iterações', fontsize=12, fontweight='bold')
    ax2.set_title('Iterações até Convergência', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(dataset_labels)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, iter_val in zip(bars2, iters):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(iter_val)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('performance_analysis_serial.png', dpi=300, bbox_inches='tight')
    print("Gráfico salvo: performance_analysis_serial.png")
    
    return times, sses, iters

def print_analysis_report(results, times, sses, iters):
    print("\n" + "="*60)
    print("ANÁLISE DE DESEMPENHO - K-MEANS SERIAL")
    print("="*60)
    
    datasets = list(results.keys())
    
    for i, dataset_name in enumerate(datasets):
        print(f"\n {dataset_name}")
        print("-" * 60)
        print(f"  Tempo:      {times[i]:8.1f} ms")
        print(f"  SSE final:  {sses[i]:8.2f}")
        print(f"  Iterações:  {int(iters[i])}")
    
    print("\n" + "="*60)
    print("OBSERVAÇÕES")
    print("="*60)
    print("""
1. Estes são os resultados baseline para comparação com versões paralelas
2. O tempo aumenta proporcionalmente ao tamanho do dataset
3. SSE e iterações dependem da distribuição dos dados e centróides iniciais
4. Use estes valores para calcular speedup das versões paralelas
""")

def main():
    print("K-means Serial - Análise de Desempenho")
    print("=" * 60)
    
    if not os.path.exists('run_tests.sh'):
        print("Erro: Script run_tests.sh não encontrado!")
        print("Certifique-se de estar na pasta serial/")
        sys.exit(1)
    
    test_output = run_tests_and_capture_results()
    if not test_output:
        print("Falha ao executar testes!")
        sys.exit(1)
    
    results = parse_test_results(test_output)
    if not results:
        print("Falha ao analisar resultados!")
        sys.exit(1)
    
    times, sses, iters = create_performance_charts(results)
    print_analysis_report(results, times, sses, iters)
    
    print("\nAnálise concluída com sucesso!")
    print("Arquivos gerados:")
    print("   - performance_analysis_serial.png (gráficos)")
    print("   - assign_serial_*.csv (resultados de clustering)")
    print("   - centroids_serial_*.csv (centróides finais)")

if __name__ == "__main__":
    main()
