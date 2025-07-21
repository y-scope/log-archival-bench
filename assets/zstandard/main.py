#!/usr/bin/env python3

import sys
import subprocess
import datetime
import json

from src.template import ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
ASSETS_DIR: The directory this file resides in, inside the container
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

ZST_FILE_PATH = "/home/compressed.zst"
DECOMPRESSED_FILE_PATH = "/home/decompressed.log"
class zstandard_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage(ZST_FILE_PATH)

    def launch(self):
        """
        Runs the benchmarked tool
        """
        pass

    def ingest(self):
        """
        Ingests the dataset at self.datasets_path
        """
        self.docker_execute(f"zstd -3 -o {ZST_FILE_PATH} {self.datasets_path}")
    
    def search(self, query):
        """
        Searches an already-ingested dataset with query, which is populated within config.yaml
        """
        assert query == "notasearch"

        self.docker_execute(f"zstd -d -f -k {ZST_FILE_PATH} -o {DECOMPRESSED_FILE_PATH}")
        return 0
    def bench_search(self, cold=True):
        if not cold:
            logger.info("hot run and cold run are the same (decompression), skipping")
            return

        self.bench_start(ingest=False)
        self.docker_execute(f"zstd -d -f -k {ZST_FILE_PATH} -o {DECOMPRESSED_FILE_PATH}")
        self.bench_stop()

        logger.info("Decompression done")
        try:
            self.docker_execute(f"cmp -s {DECOMPRESSED_FILE_PATH} {self.datasets_path}")
            failed = False
        except subprocess.CalledProcessError:
            failed = True
        
        if failed:
            logger.warning("Decompression failed")

        ingestout = self.output[self.dataset_name][json.dumps(self.properties)]["ingest"]

        ingestout["decompress_time_taken_s"] = self.bench_info['time_taken']
        ingestout["decompress_memory_average_B"] = self.bench_info['memory_average']
        ingestout["decompress_failed"] = "yes" if failed else "no"
        ingestout["decompress_start_time"] = datetime.datetime.fromtimestamp(self.bench_info['start_time']).strftime('%Y-%m-%d %H:%M:%S')

        self.output.write()


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
        self.docker_execute(f"rm -rf {ZST_FILE_PATH}")
        self.docker_execute(f"rm -rf {DECOMPRESSED_FILE_PATH}")

    @property
    def terminate_procs(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        return []

    def run_applicable(self, dataset_name):
        self.run_everything()


def main():
    bench = zstandard_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
