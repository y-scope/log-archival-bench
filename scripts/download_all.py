#!/usr/bin/env python3

import os
import yaml
from pathlib import Path

current_dir = Path(os.getcwd())
parent_dir = Path(os.path.realpath(__file__)).parent.parent

if current_dir != parent_dir:
    raise Exception(f"Script can only be run in {parent_dir}")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]


def chdir(path):
    print(f'cd {path}')
    os.chdir(str(path))

def system(command):
    print(command)
    os.system(command)

for bench_target in bench_target_dirs:
    with open(str(bench_target / "metadata.yaml")) as file:
        bench_meta = yaml.safe_load(file)

    chdir(bench_target)
    system(f"curl -o output.tar.gz {bench_meta['source']}")
    system("mkdir output")
    system("tar -xvzf output.tar.gz -C output --strip-components=1")

    outputdir = bench_target / "output"

    system("awk 'FNR==1 && NR!=1 { print \"\" } { print }' " + str(outputdir) + "/* > " + bench_meta['normal_log'])
    system("rm -r output.tar.gz")
    system("rm -r output")

    system(f"sed -i '/^$/d' {bench_meta['normal_log']}")

    chdir(str(data_dir))
    system(f"python3 cleankeys.py {str(bench_target / bench_meta['normal_log'])} {str(bench_target / bench_meta['cleaned_log'])}")
