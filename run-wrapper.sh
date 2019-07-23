#!/usr/bin/env bash

set -e
lzdir=$(dirname $0)

echo 'cleaning profile directory'
rm /data/data/com.termux/simpleperf_data/*
echo 'cleaning run directory'
rm -rf /sdcard/run
mkdir /sdcard/run
echo 'running benchmarks'
$lzdir/run.sh 2>&1 | tee /sdcard/run/log.txt
mv /data/data/com.termux/simpleperf_data/* /sdcard/run
pushd /sdcard
filename=run-$(date +%Y-%M-%d-%H-%M-%S).tar.gz
tar czf $filename run
popd
echo /sdcard/$filename
