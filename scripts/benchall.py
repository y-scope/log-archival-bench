#!/usr/bin/env python3

from assets.clp_s.main import clp_s_bench
from assets.clickhouse_native_json.main import clickhouse_native_json_bench
from assets.sparksql.main import sparksql_bench
from assets.openobserve.main import openobserve_bench
from assets.parquet.main import parquet_bench
from assets.zstandard.main import zstandard_bench
from assets.elasticsearch.main import elasticsearch_bench
from assets.clp_presto.main import clp_presto_bench
from src.jsonsync import JsonItem

import os
import datetime
from pathlib import Path

current_dir = Path(os.getcwd())

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]

def get_target_from_name(name):
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()
        if dataset_name == name:
            return bench_target
    raise Exception(f'{name} not found in {bench_target_dirs}')

clp_s_timestamp_keys = {
        "cockroachdb": "timestamp",
        "elasticsearch": "@timestamp",
        "postgresql": "timestamp",
        "spark-event-logs": "Timestamp",
        "mongod": r"t.\$date"
        #"mongod": "id"
        }

benchmarks = [  # benchmark object, arguments
        #(clp_s_bench, {}),
        #(clickhouse_native_json_bench, {  # give column names, don't order
        #    'manual_column_names': True,
        #    'keys': [],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': ['id'],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': ['c'],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': ['t.\\$date', 'id'],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {  # give column names, use date as primary key
        #    'manual_column_names': True,
        #    'keys': ['t.\\$date'],
        #    'additional_order_by': [],
        #    }),
        ## can even try to use json values with a default as primary or sorting
        #(clickhouse_native_json_bench, {  # give column names, order only
        #    'manual_column_names': True,
        #    'keys': [],
        #    'additional_order_by': ['id'],
        #    }),
        #(clickhouse_native_json_bench, {  # no column names
        #    'manual_column_names': False,
        #    'keys': [],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {
        #    'manual_column_names': False,
        #    'keys': ['json.id.:Int64'],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {
        #    'manual_column_names': False,
        #    'keys': [],
        #    'additional_order_by': ['json.id.:Int64'],
        #    }),
        #(clickhouse_native_json_bench, {
        #    'manual_column_names': False,
        #    'keys': ['json.c.:String'],
        #    'additional_order_by': [],
        #    }),
        #(clickhouse_native_json_bench, {
        #    'manual_column_names': False,
        #    'keys': ['json.t.\\$date.:timestamp'],
        #    'additional_order_by': [],
        #    }),

        (sparksql_bench, {}),
        (openobserve_bench, {}),
        (parquet_bench, {'mode': 'json string'}),
        (parquet_bench, {'mode': 'pairwise arrays'}),
        (zstandard_bench, {}),
        (elasticsearch_bench, {}),
        #(clp_presto_bench, {}),
    ]

def run(bencher, kwargs, bench_target):
    dataset_name = 'error when finding dataset name'
    try:
        dataset_name = os.path.basename(bench_target.resolve()).strip()

        if bencher == clp_s_bench or bencher == clp_presto_bench:  # give additional parameters according to dataset name
            kwargs["timestamp_key"] = clp_s_timestamp_keys[dataset_name]

        # benchmark clp_presto on the cleaned (no spaces) mongod dataset
        if bencher == clp_presto_bench and dataset_name == 'mongod':
            kwargs["dataset_variation"] = "mongod.log.clean"

        print(f'Benchmarking {bencher.__name__} ({kwargs}) on dataset {dataset_name}')

        bench = bencher(bench_target, **kwargs)
        bench.run_applicable(dataset_name)
        #bench.run_everything(['ingest', 'cold'])
    except Exception as e:
        with open((current_dir / 'exceptions.log').resolve(), 'a') as file:
            file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {bencher.__name__} with argument {kwargs} failed on dataset {dataset_name}: {type(e).__name__}: {str(e)}\n")
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {bencher.__name__} with argument {kwargs} failed on dataset {dataset_name}: {type(e).__name__}: {str(e)}")

for bencher, kwargs in benchmarks:
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()

        #if dataset_name != 'mongod':  # only use mongod for now
        #    continue
        run(bencher, kwargs, bench_target)

#run(zstandard_bench, {}, get_target_from_name('spark-event-logs'))
#run(parquet_bench, {'mode': 'columns values'}, get_target_from_name('mongod'))
#run(clp_s_bench, {}, get_target_from_name('mongod'))  # rerun mongod because it was using id
