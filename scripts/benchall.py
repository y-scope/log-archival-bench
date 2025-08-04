#!/usr/bin/env python3

from assets.clp.main import clp_bench
from assets.clickhouse.main import clickhouse_bench
from assets.sparksql.main import sparksql_bench
from assets.presto_parquet.main import parquet_bench
from assets.zstandard.main import zstandard_bench
from assets.elasticsearch.main import elasticsearch_bench
from assets.presto_clp.main import presto_clp_bench
from assets.overhead_test.main import overhead_test_bench
from assets.gzip.main import gzip_bench
from src.jsonsync import JsonItem

import os
import sys
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


benchmarks = [  # benchmark object, arguments
        #(clp_bench, {}),
        #(clickhouse_bench, {
        #    'manual_column_names': False,
        #    'keys': [],
        #    'additional_order_by': [],
        #    'timestamp_key': True
        #    }),
        #(presto_clp_bench, {
        #    'dataset_variation': "cleaned_log"
        #    }),
        #(parquet_bench, {'mode': 'json string'}),
        #(parquet_bench, {'mode': 'pairwise arrays'}),
        (elasticsearch_bench, {}),
        #(overhead_test_bench, {}),
        #(zstandard_bench, {}),
        #(sparksql_bench, {}),
        #(gzip_bench, {}),
    ]

def run(bencher, kwargs, bench_target, attach=False, attach_on_error=False):
    dataset_name = 'error when finding dataset name'
    bench = None
    try:
        dataset_name = os.path.basename(bench_target.resolve()).strip()
        # benchmark clp_presto on the cleaned (no spaces) datasets

        print(f'Benchmarking {bencher.__name__} ({kwargs}) on dataset {dataset_name}')

        bench = bencher(bench_target, **kwargs)
        bench.attach = attach
        bench.run_applicable(dataset_name)
        #bench.run_everything([])
        #bench.run_everything(['ingest', 'cold'])
    except Exception as e:
        statement = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {bencher.__name__} with argument {kwargs} failed on dataset {dataset_name}: {type(e).__name__}: {str(e)}"
        with open((current_dir / 'exceptions.log').resolve(), 'a') as file:
            file.write(f"{statement}\n")
        print(statement)
        if attach or attach_on_error:
            if bench is not None:
                bench.docker_attach()
        else:
            pass

for bencher, kwargs in benchmarks:
    for bench_target in bench_target_dirs:
        dataset_name = os.path.basename(bench_target.resolve()).strip()
        
        if len(sys.argv) > 1:
            if dataset_name != sys.argv[1].strip():
                continue
        #run(bencher, kwargs, bench_target)
        run(bencher, kwargs, bench_target, attach_on_error=True)
        #run(bencher, kwargs, bench_target, attach=True)

#run(sparksql_bench, {}, get_target_from_name('mongod'))
