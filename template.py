import pathlib
import subprocess
import logging
import os
import yaml
import json
from jsonsync import JsonSyncDict

WORK_DIR = "/home"
ASSETS_DIR = f"{WORK_DIR}/assets"
DATASETS_DIR = f"{WORK_DIR}/datasets"
DATASETS_PATH = f"{DATASETS_DIR}/mongod.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Benchmark:
    def __init__(self, dataset):
        self.dataset = dataset
        assert os.path.exists(f"{self.script_dir}/Dockerfile")
        assert os.path.exists(f"{self.script_dir}/config.yaml")
        self.output = JsonSyncDict(f"{self.script_dir}/output.json")

    @property
    def container_name(self):
        raise NotImplementedError

    @property
    def script_dir(self):
        return pathlib.Path(__file__).parent.resolve()

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
                [
                    'docker build',
                    f'--tag {self.container_name}',
                    f'{self.script_dir}',
                ],
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
                '--cpuset-cpus="0,1,2,3"'
                '--memory=8g'
                '--memory-swap=8g'
                ]

        if background:
            interactive_param = [
                    '--it',
                    f'--workdir {WORK_DIR}'
                    ]
            interactive_exec = f'bash -c "cd {WORK_DIR} && /bin/bash -l"'
        else:
            interactive_param = []
            interactive_exec = ''

        result = subprocess.run(
                [
                    'docker run',
                    '--privileged',
                    '--rm',
                    '--network host',
                    f'--name {self.container_name}',
                    f'--mount "type=bind,src={self.script_dir},dst={ASSETS_DIR}"',
                    f'--mount "type=bind,src={self.dataset},dst={DATASETS_DIR}"',
                    *mount_param,
                    *limits_param,
                    *interactive_param,
                    f"{self.container_name}",
                    interactive_exec,
                ],
                shell = True,
                check = True
                )
        logger.debug(result)

    def docker_execute(self, statement):
        if type(statement) is str:
            pass
        if type(statement) is list:
            statement = ' '.join(statement)

        result = subprocess.run(
                f"docker exec {self.container_name} bash {statement}",
                stdout=subprocess.PIPE,
                shell = True,
                check = True
                )
        logger.debug(result)
        return result.stdout.decode("utf-8")


CLP_OUT_PATH = f"{WORK_DIR}/archives"
CLP_S_BINARY = "/clp/clp-s"
class clp_s_bench(Benchmark):
    def __init__(self, dataset, timestamp_key=r"t.\$date", target_encoded_size=268435456):
        super().__init__(dataset)

        logging.info("target_encoded_size:", target_encoded_size//(1024*1024), 'MB')

        self.timestamp = timestamp_key
        self.target_encoded_size = target_encoded_size

    @property
    def container_name(self):
        return "clp-clp-bench"

    @property
    def compressed_size(self):
        return self.get_disk_usage(CLP_OUT_PATH)

    def ingest(self):
        self.docker_execute([
            CLP_S_BINARY,
            'c',
            f'--timestamp-key {self.timestamp}',
            f'--target-encoded-size {self.target_encoded_size}',
            CLP_OUT_PATH,
            DATASETS_PATH,
            ])
    
    def _search(self, query):
        return self.docker_execute([
            CLP_S_BINARY,
            's',
            CLP_OUT_PATH,
            query,

            "|",
            "wc -l"
            ])

    def search(self):

