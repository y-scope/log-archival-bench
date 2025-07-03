#!/usr/bin/env python3

from assets.clp_s.main import clp_s_bench
from assets.clickhouse_native_json.main import clickhouse_native_json_bench

import os
from pathlib import Path

current_dir = Path(os.getcwd())

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]


benchmarks = [clp_s_bench, clickhouse_native_json_bench]
#benchmarks = [clickhouse_native_json_bench]
mongod_only = [clickhouse_native_json_bench]

for bencher in benchmarks:
    bench = bencher("mongod")
    bench.run_everything()

    if bencher not in mongod_only:
        for bench_target in bench_target_dirs:
            bench = bencher(bench_target)
            bench.run_ingest()
