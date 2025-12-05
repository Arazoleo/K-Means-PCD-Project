#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <sys/time.h>
#include <mpi.h>

double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec * 1e-6;
}

int read_data(const char *filename, double **data, int *n) {
    FILE *f = fopen(filename, "r");
    if (!f) return 0;
    
    *n = 0;
    int capacity = 1000;
    *data = (double*)malloc(capacity * sizeof(double));
    
    while (fscanf(f, "%lf", &(*data)[*n]) == 1) {
        (*n)++;
        if (*n >= capacity) {
            capacity *= 2;
            *data = (double*)realloc(*data, capacity * sizeof(double));
        }
    }
    fclose(f);
    return 1;
}

int read_centroids(const char *filename, double **centroids, int *k) {
    return read_data(filename, centroids, k);
}

void assign_clusters(double *data, int n, double *centroids, int k, 
                     int *assign, double *sse) {
    *sse = 0.0;
    for (int i = 0; i < n; i++) {
        double min_dist = fabs(data[i] - centroids[0]);
        int best = 0;
        for (int c = 1; c < k; c++) {
            double dist = fabs(data[i] - centroids[c]);
            if (dist < min_dist) {
                min_dist = dist;
                best = c;
            }
        }
        assign[i] = best;
        *sse += min_dist * min_dist;
    }
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (argc < 5) {
        if (rank == 0) {
            printf("Uso: %s <dados.csv> <centroides.csv> <max_iter> <epsilon> [assign.csv] [centroids.csv]\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }
    
    const char *data_file = argv[1];
    const char *cent_file = argv[2];
    int max_iter = atoi(argv[3]);
    double epsilon = atof(argv[4]);
    const char *assign_out = (argc > 5) ? argv[5] : NULL;
    const char *cent_out = (argc > 6) ? argv[6] : NULL;
    
    double *data = NULL, *centroids = NULL;
    int n = 0, k = 0;
    int *assign = NULL;
    
    if (rank == 0) {
        if (!read_data(data_file, &data, &n)) {
            printf("Erro ao ler %s\n", data_file);
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        if (!read_centroids(cent_file, &centroids, &k)) {
            printf("Erro ao ler %s\n", cent_file);
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
    }
    
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&k, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    if (rank != 0) {
        centroids = (double*)malloc(k * sizeof(double));
    }
    MPI_Bcast(centroids, k, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    
    int *sendcounts = (int*)malloc(size * sizeof(int));
    int *displs = (int*)malloc(size * sizeof(int));
    
    int base = n / size;
    int remainder = n % size;
    
    for (int i = 0; i < size; i++) {
        sendcounts[i] = base + (i < remainder ? 1 : 0);
        displs[i] = (i == 0) ? 0 : displs[i-1] + sendcounts[i-1];
    }
    
    int local_n = sendcounts[rank];
    double *local_data = (double*)malloc(local_n * sizeof(double));
    int *local_assign = (int*)malloc(local_n * sizeof(int));
    
    MPI_Scatterv(data, sendcounts, displs, MPI_DOUBLE,
                 local_data, local_n, MPI_DOUBLE,
                 0, MPI_COMM_WORLD);
    
    double start_time = get_time();
    
    int iter;
    for (iter = 0; iter < max_iter; iter++) {
        double local_sse = 0.0;
        assign_clusters(local_data, local_n, centroids, k, local_assign, &local_sse);
        
        double global_sse = 0.0;
        MPI_Reduce(&local_sse, &global_sse, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
        
        double *sum_local = (double*)calloc(k, sizeof(double));
        int *cnt_local = (int*)calloc(k, sizeof(int));
        
        for (int i = 0; i < local_n; i++) {
            int c = local_assign[i];
            sum_local[c] += local_data[i];
            cnt_local[c]++;
        }
        
        double *sum_global = (double*)malloc(k * sizeof(double));
        int *cnt_global = (int*)malloc(k * sizeof(int));
        
        MPI_Allreduce(sum_local, sum_global, k, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        MPI_Allreduce(cnt_local, cnt_global, k, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
        
        double max_delta = 0.0;
        for (int c = 0; c < k; c++) {
            if (cnt_global[c] > 0) {
                double new_cent = sum_global[c] / cnt_global[c];
                double delta = fabs(new_cent - centroids[c]);
                if (delta > max_delta) max_delta = delta;
                centroids[c] = new_cent;
            }
        }
        
        free(sum_local);
        free(cnt_local);
        free(sum_global);
        free(cnt_global);
        
        int converged = (max_delta < epsilon) ? 1 : 0;
        MPI_Bcast(&converged, 1, MPI_INT, 0, MPI_COMM_WORLD);
        
        if (converged) {
            iter++;
            break;
        }
    }
    
    double end_time = get_time();
    double elapsed = (end_time - start_time) * 1000.0;
    
    if (rank == 0) {
        assign = (int*)malloc(n * sizeof(int));
    }
    
    MPI_Gatherv(local_assign, local_n, MPI_INT,
                assign, sendcounts, displs, MPI_INT,
                0, MPI_COMM_WORLD);
    
    double final_sse = 0.0;
    if (rank == 0) {
        for (int i = 0; i < n; i++) {
            double dist = fabs(data[i] - centroids[assign[i]]);
            final_sse += dist * dist;
        }
    }
    
    if (rank == 0) {
        printf("\n");
        printf("K-means 1D (MPI)\n");
        printf("Processos: %d\n", size);
        printf("N=%d K=%d max_iter=%d eps=%e\n", n, k, max_iter, epsilon);
        printf("Iterações: %d | SSE final: %.6f | Tempo: %.1f ms\n", iter, final_sse, elapsed);
        printf("\n");
        
        if (assign_out) {
            FILE *f = fopen(assign_out, "w");
            if (f) {
                for (int i = 0; i < n; i++) {
                    fprintf(f, "%d\n", assign[i]);
                }
                fclose(f);
            }
        }
        
        if (cent_out) {
            FILE *f = fopen(cent_out, "w");
            if (f) {
                for (int c = 0; c < k; c++) {
                    fprintf(f, "%.6f\n", centroids[c]);
                }
                fclose(f);
            }
        }
        
        free(assign);
        free(data);
    }
    
    free(local_data);
    free(local_assign);
    free(centroids);
    free(sendcounts);
    free(displs);
    
    MPI_Finalize();
    return 0;
}
