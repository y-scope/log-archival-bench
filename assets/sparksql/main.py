#!/usr/bin/env python3

import sys

from src.template import ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

SPARKSQL_STORAGE = "/data/mongod"
class sparksql_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

        self.properties['note'] = "cluster"  # information about passed parameters to output

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage(f"{SPARKSQL_STORAGE}")

    def launch(self):
        """
        Runs the benchmarked tool
        """
        self.docker_execute("/opt/spark/sbin/start-master.sh -h 0.0.0.0")
        self.docker_execute("/opt/spark/sbin/start-worker.sh 127.0.0.1:7077")
        self.wait_for_port(7077)
        self.wait_for_port(8080)
        self.wait_for_port(8081)

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        self.docker_execute([
            f"python3 {ASSETS_DIR}/ingest.py {self.datasets_path} {SPARKSQL_STORAGE}"
            ])
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        return self.docker_execute([
            f"python3 {ASSETS_DIR}/search.py {query} {SPARKSQL_STORAGE}"
            ]).split('\n')[-1]

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.docker_execute(f"mkdir -p {SPARKSQL_STORAGE}")
        self.docker_execute(f"rm -r {SPARKSQL_STORAGE}")

    def terminate(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        self.docker_execute("pkill -f /opt/java/openjdk/bin/java")
        self.wait_for_port(7077, waitclose=True)
        self.wait_for_port(8080, waitclose=True)
        self.wait_for_port(8081, waitclose=True)


def main():
    bench = sparksql_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
