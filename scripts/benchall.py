#!/usr/bin/env python3

from assets.clp_s.main import clp_s_bench
from assets.clickhouse_native_json.main import clickhouse_native_json_bench
from assets.sparksql.main import sparksql_bench
from assets.openobserve.main import openobserve_bench
from assets.parquet.main import parquet_bench
from assets.zstandard.main import zstandard_bench
from assets.elasticsearch.main import elasticsearch_bench

import os
from pathlib import Path

current_dir = Path(os.getcwd())

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]

clp_s_timestamp_keys = {
        "cockroachdb": "timestamp",
        "elasticsearch": "@timestamp",
        "postgresql": "timestamp",
        "spark-event-logs": "Timestamp",
        #"mongod": r"t.\$date"
        "mongod": "id"
        }

benchmarks = [  # benchmark object, arguments
        #(clp_s_bench, {"timestamp_key": "id"}),
        #(clp_s_bench, {"timestamp_key": r"t.\$date"}),
        #(clp_s_bench, {}),
        #(clickhouse_native_json_bench, {  # give column names, don't order
        #    'manual_column_names': True,
        #    'keys': set(),
        #    'additional_order_by': set(),
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': {'id'},
        #    'additional_order_by': set(),
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': {'c'},
        #    'additional_order_by': set(),
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': {'t.\\$date', 'id'},
        #    'additional_order_by': set(),
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, use date as primary key
        #    'manual_column_names': True,
        #    'keys': {'t.\\$date'},
        #    'additional_order_by': set(),
        #    }),
        ## can even try to use json values with a default as primary or sorting
        #(clickhouse_native_json_bench, {  # give column names, order only
        #    'manual_column_names': True,
        #    'keys': set(),
        #    'additional_order_by': {'id'},
        #    }),
        #(clickhouse_native_json_bench, {  # no column names
        #    'manual_column_names': False,
        #    'keys': set(),
        #    'additional_order_by': set(),
        #    }),
        #(sparksql_bench, {}),
        #(openobserve_bench, {}),
        #(parquet_bench, {'mode': 'json string'}),
        #(parquet_bench, {'mode': 'columns values'}),
        (zstandard_bench, {}),
        (elasticsearch_bench, {}),
    ]

for bencher, kwargs in benchmarks:
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()

        if dataset_name != 'mongod':  # only use mongod for now
            continue

        #if bencher == clp_s_bench and dataset_name != 'mongod':
        if bencher == clp_s_bench:  # give additional parameters according to dataset name
            kwargs["timestamp_key"] = clp_s_timestamp_keys[dataset_name]

        bench = bencher(bench_target, **kwargs)
        bench.run_applicable(dataset_name)
        #bench.run_everything(['ingest', 'cold'])
