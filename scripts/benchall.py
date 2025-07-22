#!/usr/bin/env python3

from assets.clp_s.main import clp_s_bench
from assets.clickhouse_native_json.main import clickhouse_native_json_bench
from assets.sparksql.main import sparksql_bench
from assets.openobserve.main import openobserve_bench
from assets.parquet.main import parquet_bench
from assets.zstandard.main import zstandard_bench
from assets.elasticsearch.main import elasticsearch_bench
from assets.clp_presto.main import clp_presto_bench
from assets.overhead_test.main import overhead_test_bench
from assets.gzip.main import gzip_bench
from src.jsonsync import JsonItem

import os
import datetime
from pathlib import Path

current_dir = Path(os.getcwd())
parent_dir = Path(os.path.realpath(__file__)).parent.parent

if current_dir != parent_dir:
    raise Exception(f"Script can only be run in {parent_dir}")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]

def get_target_from_name(name):
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()
        if dataset_name == name:
            return bench_target
    raise Exception(f'{name} not found in {bench_target_dirs}')

#clp_s_timestamp_keys = {
#        "cockroachdb": "timestamp",
#        "elasticsearch": "@timestamp",
#        "postgresql": "timestamp",
#        "spark-event-logs": "Timestamp",
#        "mongod": r"t.\$date"
#        }
#clickhouse_keys = {
#        "cockroachdb": "timestamp",
#        "elasticsearch": '"@timestamp"',  # @ is a special character in clickhouse
#        "postgresql": "timestamp",
#        "spark-event-logs": "Timestamp",
#        "mongod": "t.$date"
#        }

benchmarks = [  # benchmark object, arguments
        #(clp_s_bench, {}),
        #(clickhouse_native_json_bench, {  # give column names, order and primary key
        #    'manual_column_names': True,
        #    'keys': ['id'],
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
        #(clickhouse_native_json_bench, {
        #    'manual_column_names': False,
        #    'keys': [],
        #    'additional_order_by': [],
        #    'timestamp_key': True
        #    }),
        (clp_presto_bench, {
            'dataset_variation': "cleaned_log"
            }),
        #(parquet_bench, {'mode': 'json string'}),
        #(parquet_bench, {'mode': 'pairwise arrays'}),
        #(elasticsearch_bench, {}),
        #(overhead_test_bench, {}),
        #(zstandard_bench, {}),
        #(sparksql_bench, {}),
        #(openobserve_bench, {
        #    #'dataset_variation': "cleaned_log"
        #    'dataset_variation': "base32_log"
        #    }),
        #(gzip_bench, {}),
    ]

def run(bencher, kwargs, bench_target, attach=False):
    dataset_name = 'error when finding dataset name'
    bench = None
    try:
        dataset_name = os.path.basename(bench_target.resolve()).strip()

        #if bencher == clp_s_bench or bencher == clp_presto_bench:  # give additional parameters according to dataset name
        #    kwargs["timestamp_key"] = clp_s_timestamp_keys[dataset_name]
        #
        #if bencher == clickhouse_native_json_bench and (not kwargs["manual_column_names"]):  # additional parameters for clickhouse too
        #    kwargs["keys"] = [f"json.{clickhouse_keys[dataset_name]}.:timestamp"]


        # benchmark clp_presto on the cleaned (no spaces) datasets

        print(f'Benchmarking {bencher.__name__} ({kwargs}) on dataset {dataset_name}')

        bench = bencher(bench_target, **kwargs)
        bench.attach = attach
        bench.run_applicable(dataset_name)
        #bench.run_everything(['ingest', 'cold'])
    except Exception as e:
        statement = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {bencher.__name__} with argument {kwargs} failed on dataset {dataset_name}: {type(e).__name__}: {str(e)}"
        with open((current_dir / 'exceptions.log').resolve(), 'a') as file:
            file.write(f"{statement}\n")
        print(statement)
        if attach:
            if bench is not None:
                bench.docker_attach()
        else:
            pass
            #raise e

for bencher, kwargs in benchmarks:
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()

        if dataset_name != 'mongod': # only use mongod for now
            continue
        run(bencher, kwargs, bench_target)
        #run(bencher, kwargs, bench_target, attach=True)

#run(openobserve_bench, {}, get_target_from_name('elasticsearch'), attach=True)
#run(openobserve_bench, {}, get_target_from_name('mongod'))
#run(openobserve_bench, {}, get_target_from_name('spark-event-logs'), attach=True)
#run(openobserve_bench, {}, get_target_from_name('cockroachdb'))
#run(openobserve_bench, {}, get_target_from_name('postgresql'))
#run(sparksql_bench, {}, get_target_from_name('mongod'))
