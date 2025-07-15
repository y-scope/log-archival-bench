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

class overhead_test_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage("/home")

    def launch(self):
        """
        Runs the benchmarked tool
        """
        self.docker_execute('sleep 5')

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        #print(self.datasets_path)
        self.docker_execute('sleep 15')
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        #print(query)
        self.docker_execute('sleep 15')
        return 15

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
        self.docker_execute('sleep 5')

    @property
    def terminate_procs(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        return []
    
    def run_applicable(self, dataset_name):
        if dataset_name == 'mongod':
            self.run_everything()
        else:
            logger.info('overhead test only runs on mongod, does not interact with dataset')


def main():
    bench = overhead_test_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
