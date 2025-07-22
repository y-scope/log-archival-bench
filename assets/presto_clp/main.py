#!/usr/bin/env python3

import sys
import time
import os

from src.template import ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
ASSETS_DIR: The directory this file resides in, inside the container
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

CLP_PRESTO_CONTAINER_STORAGE = "/home/clp-json-x86_64"
CLP_PRESTO_HOST_STORAGE = os.path.abspath(os.path.expanduser("~/clp-json-x86_64-v0.4.0-dev"))
SQL_PASSWORD = "wqEGPyBdx_w"
HOST_IP = "127.0.0.1"
class clp_presto_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset, dataset_variation='cleaned_log'):
        super().__init__(dataset, dataset_variation=dataset_variation)

        timestamp_key = self.dataset_meta['timestamp'].replace("$", r"\$")

        self.properties['note'] = "ingestion data unreliable"
        self.timestamp = timestamp_key

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage(f"{CLP_PRESTO_CONTAINER_STORAGE}/var/data/archives/default")

    @property
    def mount_points(self):
        return {
            f"{self.script_dir}/include": "/home/include",
            CLP_PRESTO_HOST_STORAGE: CLP_PRESTO_CONTAINER_STORAGE,
        }

    def launch(self):
        """
        Runs the benchmarked tool
        """
        os.system(f"{CLP_PRESTO_HOST_STORAGE}/sbin/stop-clp.sh -f")
        os.system(f"{CLP_PRESTO_HOST_STORAGE}/sbin/start-clp.sh")
        self.docker_execute('bash -c "python3 /home/presto/presto-server/target/presto-server-0.293/bin/launcher.py run --etc-dir=/home/include/etc_coordinator"', background=True)  # needs to be run with bash -c
        self.wait_for_port(8080)
        self.docker_execute("/home/presto/presto-native-execution/_build/release/presto_cpp/main/presto_server --logtostderr=1 --etc_dir=/home/include/etc_worker", background=True)
        self.wait_for_port(7777)
        time.sleep(60)  # this needs to be more than 10

    def presto_execute(self, query, check=True):
        return self.docker_execute(f'/home/presto/presto-cli/target/presto-cli-0.293-executable.jar --catalog clp --schema default --execute "{query}"', check)

    def sql_execute(self, query, check=True):
        if query[-1] != ';':
            query = query+';'
        return self.docker_execute(f"mysql -h {HOST_IP} -P 6001 -u clp-user -p{SQL_PASSWORD} -e '{query}' clp-db", check)

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        os.system(f'{CLP_PRESTO_HOST_STORAGE}/sbin/compress.sh --timestamp-key {self.timestamp} {self.datasets_path_in_host}')
        self.sql_execute(f"UPDATE clp_datasets SET archive_storage_directory=\"{CLP_PRESTO_CONTAINER_STORAGE}/var/data/archives/default\" WHERE name=\"default\"")
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        res = self.presto_execute(f"SELECT msg, c, s, t[1], ctx, id, CAST(attr AS JSON), tags from default WHERE {query.strip()[1:-1]}").strip()
        if not res:
            return 0
        return res.count('\n') + 1

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False, shell=True)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        os.system(f"{CLP_PRESTO_HOST_STORAGE}/sbin/stop-clp.sh -f")
        self.docker_execute(f'rm -r {CLP_PRESTO_CONTAINER_STORAGE}/var/data')
        os.system(f"{CLP_PRESTO_HOST_STORAGE}/sbin/start-clp.sh")

    def terminate(self):
        self.docker_execute("pkill -f /usr/lib/jvm/java-11-openjdk-amd64/bin/java", check=False)
        self.docker_execute("pkill presto_server", check=False)
        self.wait_for_port(8080, waitclose=True)
        self.wait_for_port(7777, waitclose=True)
        os.system(f"{CLP_PRESTO_HOST_STORAGE}/sbin/stop-clp.sh -f")
        time.sleep(10)


def main():
    bench = clp_presto_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
