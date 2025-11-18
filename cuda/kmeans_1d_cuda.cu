// kmeans_1d_cuda.cu
    float *d_X=nullptr, *d_C=nullptr; int *d_assign=nullptr;
    CHECK_CUDA(cudaMalloc((void**)&d_X, sizeof(float)*N));
    CHECK_CUDA(cudaMalloc((void**)&d_C, sizeof(float)*K));
    CHECK_CUDA(cudaMalloc((void**)&d_assign, sizeof(int)*N));

    // copy X once
    CHECK_CUDA(cudaMemcpy(d_X, X.data(), sizeof(float)*N, cudaMemcpyHostToDevice));

    std::vector<int> assign(N,0);

    int grid = (N + block_size - 1) / block_size;

    // timing using chrono for total; use cudaEvents for kernel if desired
    auto t_start = std::chrono::high_resolution_clock::now();

    // main loop
    double prev_sse = 1e300;
    double sse = 0.0;
    int iters = 0;
    for(iters=0; iters<max_iter; ++iters){
        // copy current centroids to device
        CHECK_CUDA(cudaMemcpy(d_C, C.data(), sizeof(float)*K, cudaMemcpyHostToDevice));

        // launch kernel
        assign_kernel<<<grid, block_size>>>(d_X, d_C, d_assign, N, K);
        CHECK_CUDA(cudaGetLastError());

        // copy assign back
        CHECK_CUDA(cudaMemcpy(assign.data(), d_assign, sizeof(int)*N, cudaMemcpyDeviceToHost));

        // compute sse on host
        sse = compute_sse_host(X, C, assign);
        double rel = fabs(sse - prev_sse) / (prev_sse > 0.0 ? prev_sse : 1.0);
        // update centroids on host
        update_host_means(X, C, assign);

        prev_sse = sse;
        if(rel < eps) { iters++; break; }
    }

    auto t_end = std::chrono::high_resolution_clock::now();
    double total_ms = std::chrono::duration<double, std::milli>(t_end - t_start).count();

    printf("K-means 1D (CUDA assignment, host update)\n");
    printf("N=%d K=%d max_iter=%d eps=%g\n", N, K, max_iter, eps);
    printf("Iterações: %d | SSE final: %.6f | Tempo total: %.3f ms\n", iters, sse, total_ms);

    // write resultados line
    write_resultados_csv(pathOut, "cuda_assign_host", N, K, iters, sse, total_ms);

    // optionally write assign and centroids
    {
        std::ofstream fa("assign.csv");
        for(int i=0;i<N;i++) fa<<assign[i]<<"\n";
        fa.close();
        std::ofstream fc("centroids.csv");
        for(int c=0;c<K;c++) fc<<C[c]<<"\n";
        fc.close();
    }

    // free
    cudaFree(d_X); cudaFree(d_C); cudaFree(d_assign);
    return 0;
}
