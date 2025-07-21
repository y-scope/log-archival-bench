#!/usr/bin/env python3

import os
import yaml
from pathlib import Path

current_dir = Path(os.getcwd())
data_dir = current_dir / "data"

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

data_dir = current_dir / "data"
bench_target_dirs = [p for p in data_dir.iterdir() if p.is_dir()]

for bench_target in bench_target_dirs:
    with open(str(bench_target / "metadata.yaml")) as file:
        bench_meta = yaml.safe_load(file)

    os.chdir(str(bench_target))
    os.system(f"curl -o output.tar.gz {bench_meta['source']}")
    os.system("tar -xvzf output.tar.gz -C output")

    outputdir = bench_target / "output"

    os.system("awk 'FNR==1 && NR!=1 { print \"\" } { print }' " + ' '.join([str(p) for p in outputdir.iterdir() if p.is_file()]) + " > " + bench_meta['normal_log'])
    os.rmdir(str(outputdir))

    os.chdir(str(data_dir))
    os.system(f"python3 cleankeys.py {str(bench_target / bench_meta['normal_log'])} {str(bench_target / bench_meta['cleaned_log'])}")
