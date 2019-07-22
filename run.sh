#!/usr/bin/env bash

set -e
lzdir=$(dirname $0)

function run_bench {
    local method=$1
    echo -n $method, 
    date
    $lzdir/lzbench -o4 -j -e$method --sp -j ~/corpus/js/3*
}

for i in $(seq 1 2 19)
do
    run_bench zstd,$i
done

for i in $(seq 1 2 11)
do
    run_bench brotli,$i
done
