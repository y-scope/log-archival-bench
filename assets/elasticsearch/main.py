#!/usr/bin/env python3

import sys
import time

from src.template import ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
ASSETS_DIR: The directory this file resides in, inside the container
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

class elasticsearch_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset, logsdb=True):
        super().__init__(dataset)

        self.logsdb = logsdb
        
        if not logsdb:
            self.properties["notes"] = "no logsdb"

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return int(self.docker_execute(f"python3 {ASSETS_DIR}/measure-compressed-size.py"))

    def launch(self):
        """
        Runs the benchmarked tool
        """
        time.sleep(10)
        self.docker_execute(f"bash -c '{ASSETS_DIR}/launch.sh'")
        time.sleep(10)

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        if self.logsdb:
            logsdb = "anything"
        else:
            logsdb = "no_logsdb"

        self.docker_execute([
            f"python3 {ASSETS_DIR}/ingest.py {self.datasets_path} {self.dataset_meta['timestamp']} {logsdb}"
            ])
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        return self.docker_execute([
            f"python3 {ASSETS_DIR}/search.py {query}"
            ])

    def clear_cache(self):
        """
        Clears the cache within the docker container for cold run
        """
        self.docker_execute([
            f"python3 {ASSETS_DIR}/clear-cache.py"
            ])
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False, shell=True)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.docker_execute([
            f"python3 {ASSETS_DIR}/reset.py"
            ])

    @property
    def terminate_procs(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        return ['java', '/usr/share/elasticsearch/jdk/bin/java']


def main():
    bench = elasticsearch_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
