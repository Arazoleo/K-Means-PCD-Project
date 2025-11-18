#!/usr/bin/env python3

import sys
import csv
import matplotlib.pyplot as plt
import numpy as np

def read_results_file(filename):
    results = []
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    'version': row['version'],
                    'N': int(row['N']),
                    'K': int(row['K']),
                    'iterations': int(row['iterations']),
                    'sse': float(row['sse']),
                    'time_ms': float(row['time_ms'])
                })
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        return None
    return results

def calculate_speedup(results, baseline='serial'):
    baseline_time = None
    for r in results:
        if r['version'] == baseline:
            baseline_time = r['time_ms']
            break
    
    if baseline_time is None:
        print(f"Baseline '{baseline}' não encontrado!")
        return results
    
    for r in results:
        r['speedup'] = baseline_time / r['time_ms']
        r['throughput'] = r['N'] / r['time_ms']
    
    return results

def plot_comparison(results):
    versions = [r['version'] for r in results]
    times = [r['time_ms'] for r in results]
    speedups = [r.get('speedup', 1.0) for r in results]
    throughputs = [r.get('throughput', 0) for r in results]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].bar(versions, times)
    axes[0].set_ylabel('Tempo (ms)')
    axes[0].set_title('Tempo de Execução')
    axes[0].tick_params(axis='x', rotation=45)

    axes[1].bar(versions, speedups)
    axes[1].axhline(y=1.0, color='black', linestyle='--')
    axes[1].set_ylabel('Speedup')
    axes[1].set_title('Speedup vs Serial')
    axes[1].tick_params(axis='x', rotation=45)

    axes[2].bar(versions, throughputs)
    axes[2].set_ylabel('Pontos/ms')
    axes[2].set_title('Throughput')
    axes[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('cuda_comparison.png', dpi=300)
    print("Gráfico salvo: cuda_comparison.png")
    plt.show()

def print_summary(results):
    print("\n" + "="*80)
    print("RESUMO DOS RESULTADOS - K-MEANS 1D")
    print("="*80)
    print(f"{'Versão':<15} {'Tempo (ms)':<15} {'Speedup':<12} {'Throughput':<15} {'SSE':<12}")
    print("-"*80)
    
    for r in results:
        speedup = r.get('speedup', 1.0)
        throughput = r.get('throughput', 0)
        print(f"{r['version']:<15} {r['time_ms']:<15.3f} {speedup:<12.2f}x "
              f"{throughput:<15.2f} {r['sse']:<12.6f}")
    
    print("="*80)
    
    best = min(results, key=lambda x: x['time_ms'])
    print(f"\nMelhor desempenho: {best['version']} ({best['time_ms']:.3f} ms)")

    cuda_results = [r for r in results if 'cuda' in r['version'].lower()]
    if cuda_results:
        cuda = cuda_results[0]
        serial = next((r for r in results if r['version'] == 'serial'), None)
        if serial:
            efficiency = cuda['speedup'] * 100
            print(f"Eficiência CUDA: {efficiency:.2f}%")
    
    print()

def verify_correctness(results):
    sses = [r['sse'] for r in results]
    sse_std = np.std(sses)
    
    print("\n" + "="*80)
    print("VERIFICAÇÃO DE CORRETUDE")
    print("="*80)
    print(f"SSE médio: {np.mean(sses):.6f}")
    print(f"Desvio padrão SSE: {sse_std:.6e}")
    
    if sse_std < 1e-3:
        print("✓ Todos os métodos convergem para o mesmo resultado!")
    else:
        print("⚠ Diferenças significativas entre os métodos detectadas.")
    print()

def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_cuda_results.py <arquivo_resultados.csv>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    results = read_results_file(results_file)
    
    if not results:
        sys.exit(1)
    
    results = calculate_speedup(results, baseline='serial')
    
    print_summary(results)
    verify_correctness(results)
    plot_comparison(results)

if __name__ == "__main__":
    main()
