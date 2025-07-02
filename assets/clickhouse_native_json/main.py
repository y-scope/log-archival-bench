#!/usr/bin/env python3

import sys
import time

from src.template import DATASETS_PATH, Benchmark, logger
"""
DATASETS_PATH: The in-container path to the log file
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

CLICKHOUSE_COLLECTION_NAME = "clickhouse_clp_bench"
class clickhouse_native_json_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

        self.properties = "No extra configuration"  # information about passed parameters to output

    @property
    def mount_points(self):
        return {
            f"{self.script_dir}/include/config.xml": "/etc/clickhouse-server/config.d/benchconfig.xml",
            f"{self.script_dir}/include/users.xml": "/etc/clickhouse/server/users.d/benchconfig.xml",
        }

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return int(self.docker_execute([
                'clickhouse-client',
                f""" \
                --query "SELECT SUM(bytes) from system.parts \
                WHERE active AND table = '{CLICKHOUSE_COLLECTION_NAME}'" \
                """
                ]))

    def launch(self):
        """
        Runs the benchmarked tool
        """
        self.docker_execute("nohup /entrypoint.sh &")
        while self.docker_execute('clickhouse-client --query "SELECT 1"') != "1":
            time.sleep(1)

        self.docker_execute([
            'clickhouse-client',
            '--query "SET enable_json_type = 1;"'
            ])

    def ingest(self):
        """
        Ingests the dataset at DATASETS_PATH
        """
        self.docker_execute([
            'clickhouse-client',
            f""" \
            --query "INSERT INTO {CLICKHOUSE_COLLECTION_NAME} FROM INFILE '{DATASETS_PATH}' FORMAT JSON" \
            """
            ])
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        cmd = [
            'clickhouse-client',
            f""" \
            --query "SELECT * FROM {CLICKHOUSE_COLLECTION_NAME} WHERE {query.strip()[1:-1]}" \
            """,  # truncate double quotes and use single quotes for bash
            "| wc -l",
            ]
        return self.docker_execute(cmd)

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.docker_execute('clickhouse-client --query "SYSTEM DROP UNCOMPRESSED CACHE"')
        self.docker_execute('clickhouse-client --query "SYSTEM DROP MARK CACHE"')
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.docker_execute([
            'clickhouse-client',
            f'--query "DROP TABLE IF EXISTS {CLICKHOUSE_COLLECTION_NAME}"'
            ])

        # every newline here is escaped within python, the container sees this as one giant line
        # \\$date escape for escpaing "$" in bash
        self.docker_execute([
            'clickhouse-client',
            f"""\
            --query "CREATE TABLE {CLICKHOUSE_COLLECTION_NAME}( \
                t Tuple(\\$date String), \
                s String, \
                c String, \
                id int, \
                ctx String, \
                msg String, \
                attr JSON \
                ) \
            ENGINE = MergeTree \
            PRIMARY KEY (id) \
            ORDER BY (id) \
            " \
            """,
            ])

    def terminate(self):
        self.docker_execute("clickhouse-server stop >/dev/null 2>&1", check=False)


def main():
    bench = clickhouse_native_json_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()

