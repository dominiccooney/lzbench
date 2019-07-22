#!/usr/bin/env python3

import argparse
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import subprocess
import sys

simpleperf_bin = '/d2/zstd-chromium/extras/simpleperf/scripts/bin/linux/x86_64/simpleperf'


def cycles(perf_data_file):
  proc = subprocess.run([simpleperf_bin, 'report', '-i', perf_data_file], capture_output=True)
  m = re.search(r'Event count: (?P<count>\d+)', str(proc.stdout, encoding='UTF-8'))
  return int(m['count'])


def knit(input_dir):
  month_to_num = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
  }
  runs = []
  with open(os.path.join(input_dir, 'log.txt'), 'r') as log:
    for line in log:
      if line.startswith('Compressor name') or line.startswith('memcpy'):
        continue
      m = re.search(r'^(?P<options>.*),(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?P<day>\d+) (?P<hh>\d+):(?P<mm>\d+):(?P<ss>\d+)', line)
      if m:
        runs.append({
          'options': m['options'],
          'when': f'perf-{month_to_num[m["month"]]}-{m["day"]}-{m["hh"]}-{m["mm"]}-{m["ss"]}.data',
        })
      else:
        runs[-1]['results'] = line.strip().split(',')
  perf_data_files = sorted(map(os.path.basename, glob.glob(os.path.join(input_dir, 'perf-*.data'))))
  i = 0
  for run in runs:
    while i < len(perf_data_files) and perf_data_files[i] < run['when']:
      i += 1
    if i == len(perf_data_files):
      print(f'oh noes, not enough perf data files for {run}', file=sys.stderr)
    run['cycles'] = cycles(perf_data_files[i])
  return runs


def plot(runs):
  decompression_speed = np.array(list(map(lambda run: float(run['results'][2]), runs)))
  compression_ratio = np.array(list(map(lambda run: float(run['results'][5]), runs)))
  print(decompression_speed)
  print(compression_ratio)
  fig, ax = plt.subplots()
  is_brotli = np.array([run['options'].startswith('brotli') for run in runs])
  for br in [False, True]:
    index = is_brotli == br
    ax.scatter(
      compression_ratio[index], decompression_speed[index], color=br and 'brown' or 'darkgray', marker=br and '^' or 'o', label=br and 'Brotli' or 'Zstd')
  for i, run in enumerate(runs):
    ax.annotate(run['options'].split(',')[1], (compression_ratio[i] + 0.1, decompression_speed[i] - 11))
  ax.set_xlabel('Compression ratio (%)')
  ax.set_ylabel('Decompression speed')
  ax.set_title('lzbench Codec Speed')
  ax.legend()
  plt.show()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('dir')
  args = parser.parse_args()
  plot(knit(args.dir))


if __name__ == '__main__':
  main()
