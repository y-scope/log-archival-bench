import pathlib
import subprocess
import logging
import os
import yaml
import json
import time
import threading
import datetime
import sys
import shlex
from jsonsync import JsonItem

WORK_DIR = "/home"
ASSETS_DIR = f"{WORK_DIR}/assets"
DATASETS_DIR = f"{WORK_DIR}/datasets"
DATASETS_PATH = f"{DATASETS_DIR}/mongod.log"

logger = logging.getLogger(__name__)
logger.propagate = False
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logging_console_handler = logging.StreamHandler()
logging_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
logging_console_handler.setFormatter(logging_formatter)
logger.addHandler(logging_console_handler)

class Benchmark:
    def __init__(self, dataset_dir):
        self.dataset = os.path.abspath(dataset_dir)
        self.dataset_name = os.path.basename(dataset_dir)

        self.outputjson = f"{self.script_dir}/output.json"
        assert os.path.exists(f"{self.script_dir}/Dockerfile")
        assert os.path.exists(f"{self.script_dir}/config.yaml")

        self.output = JsonItem.read(self.outputjson)
        self._cached_config = None

        self.bench_info = {}
        self.properties = "default"

    @property
    def container_name(self):
        raise NotImplementedError

    @property
    def script_dir(self):
        return pathlib.Path(sys.argv[0]).parent.resolve()

    @property
    def config(self):
        if not self._cached_config:
            with open(f"{self.script_dir}/config.yaml") as file:
                self._cached_config = yaml.safe_load(file)
        return self._cached_config

    def get_disk_usage(self, path):
        return self.docker_execute([
            'du',
            path,
            '-bc',

            '|',
            r'awk "END {print\$1}"',
            ])

    @property
    def decompressed_size(self):
        return self.get_disk_usage(DATASETS_PATH)

    @property
    def compressed_size(self):
        raise NotImplementedError

    def docker_build(self):
        result = subprocess.run(
                f'docker build --tag {self.container_name} {self.script_dir}',
                shell = True,
                check = True
                )
        logger.debug(result)

    def docker_attach(self):
        result = subprocess.run(
                f'docker exec -it {self.container_name} bash',
                shell = True,
                check = True
                )
        logger.debug(result)

    def docker_run(self, background=True, mount={}):
        mount_param = [
                f'--mount "type=bind,src={key},dst={value}"'
                for key, value in mount
                ]

        limits_param = [
                '--cpus=4',
                '--memory=8g',
                '--memory-swap=8g'
                ]

        if background:
            interactive_param = [
                    '-d'
                    ]
            interactive_exec = 'bash'
        else:
            interactive_param = [
                    '-it',
                    f'--workdir {WORK_DIR}'
                    ]
            interactive_exec = f'bash -c "cd {WORK_DIR} && /bin/bash -l"'

        result = subprocess.run(
                ' '.join([
                    'docker',
                    'run',
                    '--privileged',
                    '--rm',
                    '-it',
                    '--network host',
                    f'--workdir {WORK_DIR}',
                    f'--name {self.container_name}',
                    f'--mount "type=bind,src={self.script_dir},dst={ASSETS_DIR}"',
                    f'--mount "type=bind,src={self.dataset},dst={DATASETS_DIR}"',
                    *mount_param,
                    *limits_param,
                    *interactive_param,
                    f"{self.container_name}",
                    interactive_exec,
                ]),
                shell = True,
                check = True
                )
        logger.debug(result)

    def docker_remove(self):
        result = subprocess.run(
                f'docker container stop {self.container_name}',
                shell = True,
                stdout=subprocess.DEVNULL
                )
        logger.debug(result)

    def docker_execute(self, statement, check=True):
        if type(statement) is str:
            pass
        if type(statement) is list:
            statement = ' '.join(statement)

        result = subprocess.run(
                #f"docker exec {self.container_name} bash -c \"{shlex.quote(statement)}\"",
                f"docker exec {self.container_name} bash -c {shlex.quote(statement)}",
                stdout=subprocess.PIPE,
                shell = True,
                check = check
                )
        logger.debug(result)
        return result.stdout.decode("utf-8").strip()

    def ingest(self):
        raise NotImplementedError
    def search(self, query):
        raise NotImplementedError
    def clear_cache(self):
        raise NotImplementedError
    def reset(self):
        raise NotImplementedError
    def launch(self):
        raise NotImplementedError

    @property
    def terminate_procs(self):
        return []

    def terminate(self):
        for procname in self.terminate_procs:
            self.docker_execute(f"pkill -f {procname}")

    def __bench_start(self):
        self.bench_info['start_time'] = time.time()
        self.bench_info['memory'] = []
        self.bench_info['running'] = True

        def append_memory():
            kb_to_b = 1024
            output = self.docker_execute("ps aux").split('\n')
            metric_sample = 0
            for line in output:
                process = line.strip().split()[10].strip()
                for related_process in self.config["related_processes"]:
                    if related_process.startswith(process):
                        metric_sample += int(line.strip().split()[5]) * kb_to_b
                        break
            logger.info(f"Memory used: {metric_sample//(1024*1024)} MB")
            self.bench_info['memory'].append(metric_sample)

        def poll_memory():
            while self.bench_info['running']:
                interval = int(self.config["system_metric"]["memory"]["ingest_polling_interval"])
                #time.sleep(interval)
                time.sleep(interval - (time.time() % interval))  # wait for next "5 second interval"

                if self.bench_info['running']:
                    append_memory()

        self.bench_thread = threading.Thread(
                target = poll_memory,
                daemon = True
                )
        self.bench_thread.start()

    def __bench_stop(self):
        self.bench_info['running'] = False
        self.bench_info['end_time'] = time.time()

        try:
            self.bench_info['memory_average'] = sum(self.bench_info['memory']) / len(self.bench_info['memory'])
        except ZeroDivisionError:
            self.bench_info['memory_average'] = -1  # not even 5 seconds: no benchmark

        self.bench_info['time_taken'] = self.bench_info['end_time'] - self.bench_info['start_time']

    def bench_ingest(self):
        self.launch()
        self.reset()

        self.__bench_start()
        self.ingest()
        self.__bench_stop()
        
        self.output[self.dataset_name][self.properties]['ingest'] = {
                'time_taken': self.bench_info['time_taken'],
                'memory_average_B': self.bench_info['memory_average'],
                'compressed_size': self.compressed_size,
                'decompressed_size': self.decompressed_size,
                'start_time': datetime.datetime.fromtimestamp(
                    self.bench_info['start_time']
                    ).strftime('%Y-%m-%d %H:%M:%S')
                }
        self.output.write()

        self.terminate()

    def bench_search(self, cold=True):
        self.launch()

        mode = "query_" + ("cold" if cold else "hot")
        for ind, query in enumerate(self.config["queries"]):
            
            if cold:
                self.clear_cache()
            else:
                for _ in range(self.config["hot_run_warm_up_times"]):
                    self.search(query)

            self.__bench_start()
            res = self.search(query)
            self.__bench_stop()

            logger.info(f"Query #{ind} returned {res} results.")

            self.output[self.dataset_name][self.properties][mode][ind] = {
                'time_taken': self.bench_info['time_taken'],
                'memory_average_B': self.bench_info['memory_average'],
                'result': res,
                'start_time': datetime.datetime.fromtimestamp(
                    self.bench_info['start_time']
                    ).strftime('%Y-%m-%d %H:%M:%S')
                }
            self.output.write()

        self.terminate()

    def print(self):
        print(self.output[self.dataset_name])
