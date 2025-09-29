#!/usr/bin/env python3

import sys
import subprocess
import time

from src.template import ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
ASSETS_DIR: The directory this file resides in, inside the container
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

PARQUET_DATA_PATH = "/home/hive-data"
PARQUET_SCHEMA_NAME = "bench_schema"
PARQUET_TABLE_NAME = "bench_table"
class parquet_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset, mode='json string'):
        super().__init__(dataset)

        if mode not in ('json string', 'pairwise arrays'):
            raise Exception('mode must be either "json string" or "pairwise arrays"')

        self.pairwise_arrays = False
        if mode == 'pairwise arrays':
            self.pairwise_arrays = True
            self.queries = self.config['queries_pairwise_arrays']

        if mode == 'json string':
            self.properties['mode'] = 'json string'
        elif mode == 'pairwise arrays':
            self.properties['mode'] = 'pairwise arrays, no memory restriction)'

    @property
    def limits_param(self):
        if self.pairwise_arrays:
            return [
                    '--cpus=4'
                    ]
        else:
            return [
                    '--cpus=4',
                    '--memory=8g',
                    '--memory-swap=8g'
                    ]

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage(PARQUET_DATA_PATH)

    @property
    def mount_points(self):
        return {
            f"{self.script_dir}/include": "/home/include",
        }

    def launch(self):
        """
        Runs the benchmarked tool
        """
        self.docker_execute("bash -c \"python3 /home/presto/presto-server/target/presto-server-0.293/bin/launcher.py run --etc-dir=/home/include/etc_coordinator\"", background=True)
        self.wait_for_port(8080)
        self.docker_execute("/home/presto/presto-native-execution/_build/release/presto_cpp/main/presto_server --logtostderr=1 --etc_dir=/home/include/etc_worker", background=True)
        self.wait_for_port(7777)
        time.sleep(60)  # this needs to be more than 10

    def hive_execute(self, query, check=True):
        return self.docker_execute(f'/home/presto/presto-cli/target/presto-cli-0.293-executable.jar --catalog hive --schema {PARQUET_SCHEMA_NAME} --execute "{query}"', check)

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        self.docker_execute(f'/home/presto/presto-cli/target/presto-cli-0.293-executable.jar --catalog hive --schema {PARQUET_SCHEMA_NAME} --execute "CREATE SCHEMA IF NOT EXISTS hive.{PARQUET_SCHEMA_NAME};"')

        if self.pairwise_arrays:
            self.hive_execute(f""" \
            CREATE TABLE IF NOT EXISTS hive.{PARQUET_SCHEMA_NAME}.{PARQUET_TABLE_NAME} ( \
                "string_columns" array(varchar), \
                "string_values" array(varchar), \
                "int_columns" array(varchar), \
                "int_values" array(bigint), \
                "float_columns" array(varchar), \
                "float_values" array(double), \
                "bool_columns" array(varchar), \
                "bool_values" array(boolean) \
            ) \
            WITH ( \
                format = 'PARQUET' \
            ); \
            """)
            self.docker_execute([
                f"python3 {ASSETS_DIR}/ingest_pairwise_arrays.py {self.datasets_path}"
                ])
        else:
            self.hive_execute(f""" \
            CREATE TABLE IF NOT EXISTS hive.{PARQUET_SCHEMA_NAME}.{PARQUET_TABLE_NAME} ( \
                line VARCHAR \
            ) \
            WITH ( \
                format = 'PARQUET' \
            ); \
            """)
            self.docker_execute([
                f"python3 {ASSETS_DIR}/ingest_json_string.py {self.datasets_path}"
                ])

    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        res = self.hive_execute(f"SELECT * from {PARQUET_TABLE_NAME} WHERE {query.strip()[1:-1]}").strip()
        if not res:
            return 0
        return res.count('\n') + 1

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False, shell=True)
        self.docker_execute('curl -X GET "http://localhost:7777/v1/operation/server/clearCache?type=memory"')
        self.docker_execute('curl -X GET "http://localhost:7777/v1/operation/server/clearCache?type=ssd"')

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.docker_execute(f"mkdir -p {PARQUET_DATA_PATH}")
        self.hive_execute(f"DELETE FROM {PARQUET_SCHEMA_NAME}.{PARQUET_TABLE_NAME} WHERE true;", check=False)

    def terminate(self):
        self.docker_execute("pkill -f /usr/lib/jvm/java-11-openjdk-amd64/bin/java")
        self.docker_execute("pkill presto_server")
        self.wait_for_port(8080, waitclose=True)
        self.wait_for_port(7777, waitclose=True)
        time.sleep(10)

def main():
    bench = parquet_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
