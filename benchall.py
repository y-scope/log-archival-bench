#!/usr/bin/env python3

from assets.clp_s.main import clp_s_bench
from assets.clickhouse_native_json.main import clickhouse_native_json_bench

from src.template import Benchmark

import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent

if os.path.basename(script_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

data_dir = script_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]


benchmarks = [clp_s_bench, clickhouse_native_json_bench]

for bencher in benchmarks:
    bench = bencher("mongod")
    bench.run_everything()

    for bench_target in bench_target_dirs:
        bench = bencher(bench_target)
        bench.run_ingest()
