#!/bin/bash
# test_cuda.sh - compila e roda com block sizes e registra resultados
set -e

NVCC=nvcc
SRC=kmeans_1d_cuda.cu
BIN=kmeans_1d_cuda

$NVCC -O2 $SRC -o $BIN

DATA=dados.csv
CINIT=centroides_iniciais.csv
OUT=resultados_cuda.csv

# header
if [ ! -f $OUT ]; then
  echo "version,N,K,iterations,sse,time_ms" > $OUT
fi

for BLOCK in 128 256 512; do
  echo "Run block=${BLOCK}..."
  ./$BIN $DATA $CINIT $OUT $BLOCK 50 1e-4
done

echo "Done. resultados em $OUT"