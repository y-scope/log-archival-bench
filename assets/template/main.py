#!/usr/bin/env python3

import sys

from src.template import DATASETS_PATH, WORK_DIR, Benchmark, logger
"""
DATASETS_PATH: The in-container path to the log file
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

class tool_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

        self.properties = ""  # information about passed parameters to output

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage("path/to/storage")

    def launch(self):
        """
        Runs the benchmarked tool
        """
        pass

    def ingest(self):
        """
        Ingests the dataset at DATASETS_PATH
        """
        self.docker_execute([
            ])
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        return self.docker_execute([
            ])

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
        pass

    @property
    def terminate_procs(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        return []


def main():
    bench = tool_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
