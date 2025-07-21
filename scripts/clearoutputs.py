#!/usr/bin/env python3

import os
import glob
import sys
from pathlib import Path

current_dir = Path(os.getcwd())
parent_dir = Path(os.path.realpath(__file__)).parent.parent

if current_dir != parent_dir:
    raise Exception(f"Script can only be run in {parent_dir}")

if input('Are you sure about deleting all files (y/n): ').strip() != 'y':
    print('Exiting...')
    sys.exit(0)

# Use glob to find all matching files
files_to_remove = glob.glob('assets/*/output.json')
files_to_remove += glob.glob('exceptions.log')

for file_path in files_to_remove:
    try:
        os.remove(file_path)
        print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error removing {file_path}: {e}")

