
#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>
#include <cuda_runtime.h>

#define MAX_ITER 1000
#define EPS 1e-6
#define BLOCK_SIZE 256

// Kernel para assignment: cada thread processa um ponto
__global__ void assignment_kernel(const float *X, const float *C, int *assign, 
                                  float *errors, int N, int K) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (i < N) {
        float min_dist = FLT_MAX;
        int best_c = 0;
        
        // Encontra o centróide mais próximo
        for (int c = 0; c < K; c++) {
            float dist = (X[i] - C[c]) * (X[i] - C[c]);
            if (dist < min_dist) {
                min_dist = dist;
                best_c = c;
            }
        }
        
        assign[i] = best_c;
        errors[i] = min_dist;
    }
}

void kmeans_cuda(float *X, float *C, int *assign, int N, int K, 
                 int *out_iter, float *out_sse, double *out_time) {
    // Variáveis de tempo
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    // Aloca memória na GPU
    float *d_X, *d_C, *d_errors;
    int *d_assign;
    
    cudaMalloc(&d_X, N * sizeof(float));
    cudaMalloc(&d_C, K * sizeof(float));
    cudaMalloc(&d_assign, N * sizeof(int));
    cudaMalloc(&d_errors, N * sizeof(float));
    
    // Copia dados para GPU
    cudaMemcpy(d_X, X, N * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_C, C, K * sizeof(float), cudaMemcpyHostToDevice);
    
    // Configuração do kernel
    int grid_size = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    
    // Arrays auxiliares para update na CPU
    float *sum = (float *)calloc(K, sizeof(float));
    int *cnt = (int *)calloc(K, sizeof(int));
    
    cudaEventRecord(start);
    
    int iter = 0;
    float prev_sse = FLT_MAX;
    
    for (iter = 0; iter < MAX_ITER; iter++) {
        // ASSIGNMENT na GPU
        assignment_kernel<<<grid_size, BLOCK_SIZE>>>(d_X, d_C, d_assign, d_errors, N, K);
        cudaDeviceSynchronize();
        
        // Copia assign de volta para CPU
        cudaMemcpy(assign, d_assign, N * sizeof(int), cudaMemcpyDeviceToHost);
        
        // Calcula SSE na CPU
        float *h_errors = (float *)malloc(N * sizeof(float));
        cudaMemcpy(h_errors, d_errors, N * sizeof(float), cudaMemcpyDeviceToHost);
        
        float sse = 0.0f;
        for (int i = 0; i < N; i++) {
            sse += h_errors[i];
        }
        free(h_errors);
        
        // Verifica convergência
        if (fabs(prev_sse - sse) < EPS) {
            *out_sse = sse;
            break;
        }
        prev_sse = sse;
        *out_sse = sse;
        
        // UPDATE na CPU
        for (int c = 0; c < K; c++) {
            sum[c] = 0.0f;
            cnt[c] = 0;
        }
        
        for (int i = 0; i < N; i++) {
            int c = assign[i];
            sum[c] += X[i];
            cnt[c]++;
        }
        
        for (int c = 0; c < K; c++) {
            if (cnt[c] > 0) {
                C[c] = sum[c] / cnt[c];
            } else {
                C[c] = X[0];
            }
        }
        
        // Atualiza centróides na GPU
        cudaMemcpy(d_C, C, K * sizeof(float), cudaMemcpyHostToDevice);
    }
    
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float milliseconds = 0;
    cudaEventElapsedTime(&milliseconds, start, stop);
    *out_time = milliseconds;
    *out_iter = iter;
    
    // Libera memória
    cudaFree(d_X);
    cudaFree(d_C);
    cudaFree(d_assign);
    cudaFree(d_errors);
    free(sum);
    free(cnt);
    
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
}

// Funções auxiliares para leitura/escrita de CSV
int read_csv_1col(const char *fname, float **out) {
    FILE *f = fopen(fname, "r");
    if (!f) return -1;
    
    int cap = 1024, n = 0;
    float *arr = (float *)malloc(cap * sizeof(float));
    
    while (fscanf(f, "%f", &arr[n]) == 1) {
        n++;
        if (n >= cap) {
            cap *= 2;
            arr = (float *)realloc(arr, cap * sizeof(float));
        }
    }
    fclose(f);
    *out = arr;
    return n;
}

void write_csv_1col(const char *fname, float *arr, int n) {
    FILE *f = fopen(fname, "w");
    for (int i = 0; i < n; i++) {
        fprintf(f, "%.6f\n", arr[i]);
    }
    fclose(f);
}

void write_csv_1col_int(const char *fname, int *arr, int n) {
    FILE *f = fopen(fname, "w");
    for (int i = 0; i < n; i++) {
        fprintf(f, "%d\n", arr[i]);
    }
    fclose(f);
}

int main(int argc, char **argv) {
    const char *data_file = (argc > 1) ? argv[1] : "dados.csv";
    const char *cent_file = (argc > 2) ? argv[2] : "centroides_iniciais.csv";
    
    float *X, *C;
    int N = read_csv_1col(data_file, &X);
    int K = read_csv_1col(cent_file, &C);
    
    if (N <= 0 || K <= 0) {
        fprintf(stderr, "Erro ao ler arquivos CSV\n");
        return 1;
    }
    
    int *assign = (int *)malloc(N * sizeof(int));
    int iter;
    float sse;
    double time_ms;
    
    printf("=== K-Means 1D CUDA ===\n");
    printf("N=%d, K=%d\n", N, K);
    
    kmeans_cuda(X, C, assign, N, K, &iter, &sse, &time_ms);
    
    printf("Iteracoes: %d\n", iter);
    printf("SSE final: %.6f\n", sse);
    printf("Tempo total: %.3f ms\n", time_ms);
    printf("Throughput: %.2f pontos/ms\n", N / time_ms);
    
    write_csv_1col_int("assign.csv", assign, N);
    write_csv_1col("centroids.csv", C, K);
    
    free(X);
    free(C);
    free(assign);
    
    return 0;
}