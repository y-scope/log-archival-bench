#!/usr/bin/env python3

import sys
from template import DATASETS_PATH, WORK_DIR, Benchmark, logger

CLP_OUT_PATH = f"{WORK_DIR}/archives"
CLP_S_BINARY = "/clp/clp-s"
class clp_s_bench(Benchmark):
    def __init__(self, dataset, timestamp_key=r"t.\$date", target_encoded_size=268435456):
        super().__init__(dataset)

        logger.info(f"target_encoded_size: {target_encoded_size//(1024*1024)} MB")

        self.timestamp = timestamp_key
        self.target_encoded_size = target_encoded_size

        #self.properties = f"timestamp={timestamp_key}, target_encoded_size={target_encoded_size}"
        self.properties = f"target_encoded_size={target_encoded_size}"

    @property
    def compressed_size(self):
        return self.get_disk_usage(CLP_OUT_PATH)

    def launch(self):
        self.docker_execute(f"mkdir -p {CLP_OUT_PATH}")

    def ingest(self):
        self.docker_execute([
            CLP_S_BINARY,
            'c',
            f'--timestamp-key "{self.timestamp}"',
            f'--target-encoded-size {self.target_encoded_size}',
            CLP_OUT_PATH,
            DATASETS_PATH,
            ])
    
    def search(self, query):
        return self.docker_execute([
            CLP_S_BINARY,
            's',
            CLP_OUT_PATH,
            query,

            "| wc -l"
            ])

    def clear_cache(self):
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False)

    def reset(self):
        self.docker_execute(f"rm -rf {CLP_OUT_PATH}")
        self.docker_execute(f"mkdir -p {CLP_OUT_PATH}")

    @property
    def terminate_procs(self):
        return []


if __name__ == "__main__":
    bench = clp_s_bench(sys.argv[1])
    bench.docker_remove()

    logger.info("Building container...")
    bench.docker_build()
    logger.info("Running container...")
    bench.docker_run(background=True)
    logger.info("Benchmarking ingestion...")
    bench.bench_ingest()
    logger.info("Benchmarking cold search...")
    bench.bench_search(cold=True)
    logger.info("Benchmarking hot search...")
    bench.bench_search(cold=False)
    logger.info("Removing container...")
    bench.docker_remove()

    #bench.print()

