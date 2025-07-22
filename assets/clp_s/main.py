#!/usr/bin/env python3

import sys
from src.template import WORK_DIR, Benchmark, logger

CLP_OUT_PATH = f"{WORK_DIR}/archives"
CLP_S_BINARY = "/clp/clp-s"
class clp_s_bench(Benchmark):
    def __init__(self, dataset, target_encoded_size=268435456):
        super().__init__(dataset)

        timestamp_key = self.dataset_meta['timestamp'].replace("$", r"\$")

        logger.info(f"target_encoded_size: {target_encoded_size//(1024*1024)} MB, timestamp_key: {timestamp_key}")

        self.timestamp = timestamp_key
        self.target_encoded_size = target_encoded_size

        #self.properties["timestamp"] = timestamp_key
        self.properties["target_encoded_size"] = str(target_encoded_size)
        #self.properties = f"target_encoded_size={target_encoded_size}"

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
            self.datasets_path,
            ])
    
    def search(self, query):
        res = self.docker_execute([
            CLP_S_BINARY,
            's',
            CLP_OUT_PATH,
            query,
            ])
        if not res:
            return 0
        return res.count('\n') + 1
        

    def clear_cache(self):
        self.docker_execute("sync")
        self.docker_execute("echo 1 >/proc/sys/vm/drop_caches", check=False, shell=True)

    def reset(self):
        self.docker_execute(f"rm -rf {CLP_OUT_PATH}")
        self.docker_execute(f"mkdir -p {CLP_OUT_PATH}")

    @property
    def terminate_procs(self):
        return []


def main():
    bench = clp_s_bench(sys.argv[1])
    bench.run_everything()

if __name__ == "__main__":
    main()
