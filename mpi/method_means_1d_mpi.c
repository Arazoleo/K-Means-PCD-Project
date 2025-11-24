#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <mpi.h>

static int count_rows(const char *path){
    FILE *f = fopen(path, "r");
    if(!f){ fprintf(stderr,"Erro ao abrir %s\n", path); exit(1); }
    int rows=0; char line[8192];
    while(fgets(line,sizeof(line),f)){
        int only_ws=1;
        for(char *p=line; *p; p++){
            if(*p!=' ' && *p!='\t' && *p!='\n' && *p!='\r'){ only_ws=0; break; }
        }
        if(!only_ws) rows++;
    }
    fclose(f);
    return rows;
}

static double *read_csv_1col(const char *path, int *n_out){
    int R = count_rows(path);
    if(R<=0){ fprintf(stderr,"Arquivo vazio: %s\n", path); exit(1); }
    double *A = (double*)malloc((size_t)R * sizeof(double));
    if(!A){ fprintf(stderr,"Sem memoria para %d linhas\n", R); exit(1); }

    FILE *f = fopen(path, "r");
    if(!f){ fprintf(stderr,"Erro ao abrir %s\n", path); free(A); exit(1); }

    char line[8192];
    int r=0;
    while(fgets(line,sizeof(line),f)){
        int only_ws=1;
        for(char *p=line; *p; p++){
            if(*p!=' ' && *p!='\t' && *p!='\n' && *p!='\r'){ only_ws=0; break; }
        }
        if(only_ws) continue;

        const char *delim = ",; \t";
        char *tok = strtok(line, delim);
        if(!tok){ fprintf(stderr,"Linha %d sem valor em %s\n", r+1, path); free(A); fclose(f); exit(1); }
        A[r] = atof(tok);
        r++;
        if(r>R) break;
    }
    fclose(f);
    *n_out = R;
    return A;
}

static void write_assign_csv(const char *path, const int *assign, int N){
    if(!path) return;
    FILE *f = fopen(path, "w");
    if(!f){ fprintf(stderr,"Erro ao abrir %s para escrita\n", path); return; }
    for(int i=0;i<N;i++) fprintf(f, "%d\n", assign[i]);
    fclose(f);
}

static void write_centroids_csv(const char *path, const double *C, int K){
    if(!path) return;
    FILE *f = fopen(path, "w");
    if(!f){ fprintf(stderr,"Erro ao abrir %s para escrita\n", path); return; }
    for(int c=0;c<K;c++) fprintf(f, "%.6f\n", C[c]);
    fclose(f);
}

static double assignment_step_local(const double *X_local, const double *C, int *assign_local, int N_local, int K){
    double sse_local = 0.0;
    for(int i=0;i<N_local;i++){
        int best = -1;
        double bestd = 1e300;
        for(int c=0;c<K;c++){
            double diff = X_local[i] - C[c];
            double d = diff*diff;
            if(d < bestd){ bestd = d; best = c; }
        }
        assign_local[i] = best;
        sse_local += bestd;
    }
    return sse_local;
}

static void update_step_local(const double *X_local, const int *assign_local, int N_local, int K,
                              double *sum_local, int *cnt_local){
    for(int c=0;c<K;c++){
        sum_local[c] = 0.0;
        cnt_local[c] = 0;
    }
    for(int i=0;i<N_local;i++){
        int a = assign_local[i];
        cnt_local[a] += 1;
        sum_local[a] += X_local[i];
    }
}

int main(int argc, char **argv){
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if(argc < 3){
        if(rank == 0){
            printf("Uso: mpirun -np P %s dados.csv centroides_iniciais.csv [max_iter=50] [eps=1e-4] [assign.csv] [centroids.csv]\n", argv[0]);
            printf("Obs: arquivos CSV com 1 coluna (1 valor por linha), sem cabeçalho.\n");
        }
        MPI_Finalize();
        return 1;
    }
    
    const char *pathX = argv[1];
    const char *pathC = argv[2];
    int max_iter = (argc>3)? atoi(argv[3]) : 50;
    double eps   = (argc>4)? atof(argv[4]) : 1e-4;
    const char *outAssign   = (argc>5)? argv[5] : NULL;
    const char *outCentroid = (argc>6)? argv[6] : NULL;
    
    if(max_iter <= 0 || eps <= 0.0){
        if(rank == 0) fprintf(stderr,"Parâmetros inválidos: max_iter>0 e eps>0\n");
        MPI_Finalize();
        return 1;
    }
    
    int N_total = 0, K = 0;
    double *X_total = NULL;
    double *C = NULL;
    
    if(rank == 0){
        X_total = read_csv_1col(pathX, &N_total);
        C = read_csv_1col(pathC, &K);
    }
    
    MPI_Bcast(&N_total, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&K, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    if(rank != 0){
        C = (double*)malloc((size_t)K * sizeof(double));
        if(!C){ fprintf(stderr,"Processo %d: sem memoria para C\n", rank); MPI_Abort(MPI_COMM_WORLD, 1); }
    }
    
    MPI_Bcast(C, K, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    
    int N_local = N_total / size;
    int remainder = N_total % size;
    if(rank < remainder) N_local++;
    
    int *displs = NULL;
    int *scounts = NULL;
    
    if(rank == 0){
        displs = (int*)malloc((size_t)size * sizeof(int));
        scounts = (int*)malloc((size_t)size * sizeof(int));
        if(!displs || !scounts){ fprintf(stderr,"Sem memoria para displs/scounts\n"); MPI_Abort(MPI_COMM_WORLD, 1); }
        
        int offset = 0;
        for(int p=0; p<size; p++){
            scounts[p] = N_total / size;
            if(p < remainder) scounts[p]++;
            displs[p] = offset;
            offset += scounts[p];
        }
    }
    
    double *X_local = (double*)malloc((size_t)N_local * sizeof(double));
    if(!X_local){ fprintf(stderr,"Processo %d: sem memoria para X_local\n", rank); MPI_Abort(MPI_COMM_WORLD, 1); }
    
    if(rank == 0){
        MPI_Scatterv(X_total, scounts, displs, MPI_DOUBLE, X_local, N_local, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        free(X_total);
        free(displs);
        free(scounts);
    } else {
        MPI_Scatterv(NULL, NULL, NULL, MPI_DOUBLE, X_local, N_local, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    }
    
    int *assign_local = (int*)malloc((size_t)N_local * sizeof(int));
    if(!assign_local){ fprintf(stderr,"Processo %d: sem memoria para assign_local\n", rank); MPI_Abort(MPI_COMM_WORLD, 1); }
    
    double *sum_local = (double*)malloc((size_t)K * sizeof(double));
    int *cnt_local = (int*)malloc((size_t)K * sizeof(int));
    if(!sum_local || !cnt_local){ fprintf(stderr,"Processo %d: sem memoria para sum/cnt\n", rank); MPI_Abort(MPI_COMM_WORLD, 1); }
    
    double *sum_global = (double*)malloc((size_t)K * sizeof(double));
    int *cnt_global = (int*)malloc((size_t)K * sizeof(int));
    if(!sum_global || !cnt_global){ fprintf(stderr,"Processo %d: sem memoria para sum/cnt global\n", rank); MPI_Abort(MPI_COMM_WORLD, 1); }
    
    double t0 = MPI_Wtime();
    double prev_sse = 1e300;
    double sse_global = 0.0;
    int it;
    int converged = 0;
    
    for(it=0; it<max_iter; it++){
        double sse_local = assignment_step_local(X_local, C, assign_local, N_local, K);
        
        MPI_Reduce(&sse_local, &sse_global, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
        MPI_Bcast(&sse_global, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        
        if(rank == 0){
            double rel = fabs(sse_global - prev_sse) / (prev_sse > 0.0 ? prev_sse : 1.0);
            if(rel < eps){ converged = 1; it++; }
        }
        
        MPI_Bcast(&converged, 1, MPI_INT, 0, MPI_COMM_WORLD);
        if(converged) break;
        
        update_step_local(X_local, assign_local, N_local, K, sum_local, cnt_local);
        
        MPI_Allreduce(sum_local, sum_global, K, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        MPI_Allreduce(cnt_local, cnt_global, K, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
        
        for(int c=0;c<K;c++){
            if(cnt_global[c] > 0) C[c] = sum_global[c] / (double)cnt_global[c];
            else if(rank == 0) C[c] = X_local[0];
        }
        
        MPI_Bcast(C, K, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        
        prev_sse = sse_global;
    }
    
    double t1 = MPI_Wtime();
    double ms = (t1 - t0) * 1000.0;
    
    double sse_final_local = assignment_step_local(X_local, C, assign_local, N_local, K);
    double sse_final_global = 0.0;
    MPI_Reduce(&sse_final_local, &sse_final_global, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    
    if(rank == 0){
        printf("K-means 1D (MPI)\n");
        printf("Processos: %d\n", size);
        printf("N=%d K=%d max_iter=%d eps=%g\n", N_total, K, max_iter, eps);
        printf("Iterações: %d | SSE final: %.6f | Tempo: %.1f ms\n", it, sse_final_global, ms);
    }
    
    if(rank == 0 && outAssign){
        int *assign_total = (int*)malloc((size_t)N_total * sizeof(int));
        if(assign_total){
            int *rcounts = (int*)malloc((size_t)size * sizeof(int));
            int *rdispls = (int*)malloc((size_t)size * sizeof(int));
            if(rcounts && rdispls){
                int offset = 0;
                for(int p=0; p<size; p++){
                    rcounts[p] = N_total / size;
                    if(p < remainder) rcounts[p]++;
                    rdispls[p] = offset;
                    offset += rcounts[p];
                }
                MPI_Gatherv(assign_local, N_local, MPI_INT, assign_total, rcounts, rdispls, MPI_INT, 0, MPI_COMM_WORLD);
                write_assign_csv(outAssign, assign_total, N_total);
                free(assign_total);
                free(rcounts);
                free(rdispls);
            }
        }
    } else if(rank != 0){
        MPI_Gatherv(assign_local, N_local, MPI_INT, NULL, NULL, NULL, MPI_INT, 0, MPI_COMM_WORLD);
    }
    
    if(rank == 0 && outCentroid){
        write_centroids_csv(outCentroid, C, K);
    }
    
    free(assign_local);
    free(X_local);
    free(sum_local);
    free(cnt_local);
    free(sum_global);
    free(cnt_global);
    free(C);
    
    MPI_Finalize();
    return 0;
}

