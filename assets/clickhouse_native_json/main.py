#!/usr/bin/env python3

import sys
import time
import subprocess
import shlex

from src.template import Benchmark, logger
"""
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

CLICKHOUSE_COLLECTION_NAME = "clickhouse_clp_bench"
class clickhouse_native_json_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset, manual_column_names=True, keys=[], additional_order_by=[]):
        super().__init__(dataset)

        self.manual_column_names = manual_column_names
        self.keys = keys
        self.order_by = self.keys + [i for i in additional_order_by if i not in keys]

        self.properties['manual_columns'] = str(manual_column_names)
        self.properties['keys'] = str(keys)
        self.properties['order_by'] = str(self.order_by)

        if not manual_column_names:
            self.queries = self.config["queries_automatic_json"]

    @property
    def mount_points(self):
        return {
            f"{self.script_dir}/include/config.xml": "/etc/clickhouse-server/config.d/benchconfig.xml",
            f"{self.script_dir}/include/users.xml": "/etc/clickhouse-server/users.d/benchconfig.xml",
        }

    def clickhouse_execute(self, query):
        return self.docker_execute(['clickhouse-client', '--query', shlex.quote(query)])

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        time.sleep(10)  # wait for old parts to die
        a = int(self.clickhouse_execute(f"SELECT SUM(bytes) from system.parts \
                WHERE active AND table = '{CLICKHOUSE_COLLECTION_NAME}'"))
        #print(a)
        #b = self.get_disk_usage(f"/var/lib/clickhouse/data/default/{CLICKHOUSE_COLLECTION_NAME}/*")
        #print(b)
        #c = int(self.clickhouse_execute(f"SELECT SUM(bytes) from system.parts \
        #        WHERE table = '{CLICKHOUSE_COLLECTION_NAME}'"))
        #print(c)
        return a

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

        #self.docker_execute([
        #    'clickhouse-client',
        #    '--query "SET merge_tree.old_parts_lifetime = 1;"'
        #    ])

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        format = "JSON" if self.manual_column_names else "JSONAsObject"
        self.clickhouse_execute(f"INSERT INTO {CLICKHOUSE_COLLECTION_NAME} FROM INFILE '{self.datasets_path}' FORMAT {format}")
        self.clickhouse_execute(f"OPTIMIZE TABLE {CLICKHOUSE_COLLECTION_NAME} FINAL")
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        res = self.clickhouse_execute(f"SELECT * FROM {CLICKHOUSE_COLLECTION_NAME} WHERE {query.strip()[1:-1]}")
        if not res:
            return 0
        return res.count('\n') + 1

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.clickhouse_execute("SYSTEM DROP UNCOMPRESSED CACHE")
        self.clickhouse_execute("SYSTEM DROP MARK CACHE")
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.clickhouse_execute(f"DROP TABLE IF EXISTS {CLICKHOUSE_COLLECTION_NAME}")

        # every newline here is escaped within python, the container sees this as one giant line
        # $date does not need escaping due to shlex.quote()

        if self.manual_column_names:
            table_fields = """ \
            t Tuple($date timestamp), \
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

        if (not self.manual_column_names) and self.order_by:
            params.append("SETTINGS allow_nullable_key = 1")
        params.append("SETTINGS old_parts_lifetime = 1")

        self.clickhouse_execute(f"CREATE TABLE {CLICKHOUSE_COLLECTION_NAME}({table_fields}) {' '.join(params)}")

    def terminate(self):
        self.docker_execute("clickhouse-server stop >/dev/null 2>&1", check=False)

    def run_applicable(self, dataset_name):
        if dataset_name == "mongod":
            self.run_everything()
        else:
            if self.manual_column_names or self.order_by:
                logger.info("Not running anything: clickhouse manual entry only works on mongod")
            else:
                self.run_ingest()


def main():
    bench = clickhouse_native_json_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()

