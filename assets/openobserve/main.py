#!/usr/bin/env python3

import sys
import time
import subprocess

from src.template import DATASETS_PATH, ASSETS_DIR, WORK_DIR, Benchmark, logger
"""
DATASETS_PATH: The in-container path to the log file
WORK_DIR: The in-container path to an accessible location e.g. "/home"
Benchmark: Base class for benchmarks, has docker_execute to execute command within container
logger: A logging.Logger
"""

OPENOBSERVE_DATA_DIR = f"{WORK_DIR}/data"
class openobserve_bench(Benchmark):
    # add any parameters to the tool here
    def __init__(self, dataset):
        super().__init__(dataset)

        self.properties = ""  # information about passed parameters to output

    @property
    def compressed_size(self):
        """
        Returns the size of the compressed dataset
        """
        return self.get_disk_usage(f"{OPENOBSERVE_DATA_DIR}/openobserve/stream/files/default/logs")

    def launch(self):
        """
        Runs the benchmarked tool
        """
        self.docker_execute("/openobserve init-dir -p {OPENOBSERVE_DATA_DIR}")
        self.docker_execute("nohup /openobserve &")
        self.wait_for_port(5080)

    def ingest(self):
        """
        Ingests the dataset at DATASETS_PATH
        """
        self.docker_execute([
            f"python3 {ASSETS_DIR}/ingest.py {DATASETS_PATH}"
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
        self.docker_execute("sync")
        self.docker_execute(f"rm -rf {OPENOBSERVE_DATA_DIR}/openobserve/cache")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False)

    def reset(self):
        """
        Removes a previously ingested dataset before ingesting a new one, must not throw error
        when no dataset was ingested
        """
        self.docker_execute("curl -X DELETE -u 'root@clpbench.com:password' localhost:5080/api/default/streams/clpbench1")
        while True:
            status = self.docker_execute("""\
                    curl http://localhost:5080/api/default/clpbench1/_json -i -u 'root@clpbench.com:password' -d '[]' -w "%{http_code}" -s -o /dev/null\
                    """)
            if status != "400":
                break
            else:
                time.sleep(2)

    @property
    def terminate_procs(self):
        """
        Process names as shown on `ps -aux` to terminate, reverts the launch process
        Alternatively, override the terminate(self) function in Benchmark
        """
        return ["/openobserve"]


def main():
    bench = openobserve_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
