#!/usr/bin/env python3

import os
import glob
from pathlib import Path

current_dir = Path(os.getcwd())

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

# Use glob to find all matching files
files_to_remove = glob.glob('assets/*/output.json')
files_to_remove += glob.glob('exceptions.log')

for file_path in files_to_remove:
    try:
        os.remove(file_path)
        print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error removing {file_path}: {e}")

