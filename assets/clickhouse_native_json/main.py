#!/usr/bin/env python3

import sys
import time
import subprocess

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
    def __init__(self, dataset, manual_column_names=True, keys={'id'}, additional_order_by=set()):
        if not manual_column_names:
            assert not keys and not additional_order_by

        super().__init__(dataset)

        self.manual_column_names = manual_column_names
        self.keys = list(keys)
        self.order_by = self.keys + list(additional_order_by - keys)

        self.properties = f"""\
{'manual columns' if manual_column_names else 'automatic columns'}, \
keys({','.join(self.keys)}), \
order_by({','.join(self.order_by)}) \
"""

        if not manual_column_names:
            self.config["queries"] = [
                    # override configuration queries for json
                    '"not(isNull(json.attr.tickets))"',
                    '"json.id = 22419"',
                    """\
                    "json.attr.message.msg like 'log_release%' AND json.attr.message.session_name = 'connection'"\
                    """,
                    """\
                    "json.ctx = 'initandlisten' AND (json.attr.message.msg like 'log_remove%' OR json.msg != 'WiredTigermessage')"\
                    """,
                    """\
                    "json.c = 'WTWRTLOG' and json.attr.message.ts_sec > 1679490000"\
                    """,
                    """\
                    "json.ctx = 'FlowControlRefresher' AND json.attr.numTrimmed = 0"\
                    """,
                    ]

    @property
    def mount_points(self):
        return {
            f"{self.script_dir}/include/config.xml": "/etc/clickhouse-server/config.d/benchconfig.xml",
            f"{self.script_dir}/include/users.xml": "/etc/clickhouse-server/users.d/benchconfig.xml",
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
        while True:
            try:
                val = self.docker_execute('clickhouse-client --query "SELECT 1" 2>/dev/null')
                if val != "1":
                    time.sleep(1)
                else:
                    break
            except subprocess.CalledProcessError:
                time.sleep(1)

        self.docker_execute([
            'clickhouse-client',
            '--query "SET enable_json_type = 1;"'
            ])

    def ingest(self):
        """
        Ingests the dataset at DATASETS_PATH
        """
        format = "JSON" if self.manual_column_names else "JSONAsObject"
        self.docker_execute([
            'clickhouse-client',
            f""" \
            --query "INSERT INTO {CLICKHOUSE_COLLECTION_NAME} FROM INFILE '{DATASETS_PATH}' FORMAT {format}" \
            """
            ])
        self.docker_execute(f'clickhouse-client --query "OPTIMIZE TABLE {CLICKHOUSE_COLLECTION_NAME} FINAL"')
    
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

        if self.manual_column_names:
            table_fields = """ \
            t Tuple(\\$date timestamp), \
            s String, \
            c String, \
            id int, \
            ctx String, \
            msg String, \
            attr JSON \
            """
        else:
            table_fields = """ \
            json JSON \
            """

        params = [
                "ENGINE = MergeTree"
                ]

        if not self.keys:
            params.append("PRIMARY KEY tuple()")
        else:
            params.append(f"PRIMARY KEY ({','.join(self.keys)})")

        if not self.order_by:
            params.append("ORDER BY tuple()")
        else:
            params.append(f"ORDER BY ({','.join(self.order_by)})")

        self.docker_execute([
            'clickhouse-client',
            f"""\
            --query " \
            CREATE TABLE {CLICKHOUSE_COLLECTION_NAME}({table_fields}) \
            {' '.join(params)} \
            " \
            """,
            ])

    def terminate(self):
        self.docker_execute("clickhouse-server stop >/dev/null 2>&1", check=False)

    def run_applicable(self, dataset_name):
        if dataset_name == "mongod":
            self.run_everything()
        else:
            if self.manual_column_names:
                logger.info("Not running anything: clickhouse manual entry only works on mongod")
            else:
                self.run_ingest()


def main():
    bench = clickhouse_native_json_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()

