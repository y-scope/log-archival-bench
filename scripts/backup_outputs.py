#!/usr/bin/env python3

import os
import shutil
from datetime import datetime
import sys
from pathlib import Path

# Get the current working directory
current_dir = os.getcwd()

# Add it to sys.path
if current_dir not in sys.path:
    sys.path.append(current_dir)

current_dir = Path(os.getcwd())

if os.path.basename(current_dir.resolve()) != "clp-bench-refactor":
    raise Exception("Must be run in clp-bench-refactor directory, if it was renamed, comment this line out")

def backup_outputs():
    assets_dir = "assets"
    output_base = "outputs"

    # Generate timestamp only once per run
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(output_base, timestamp_str)
    os.makedirs(backup_dir, exist_ok=True)

    for tool_name in os.listdir(assets_dir):
        tool_path = os.path.join(assets_dir, tool_name)
        output_file = os.path.join(tool_path, "output.json")

        if os.path.isdir(tool_path) and os.path.isfile(output_file):
            dest_file = os.path.join(backup_dir, f"{tool_name}.json")
            shutil.copy2(output_file, dest_file)
            print(f"Copied {output_file} → {dest_file}")

if __name__ == "__main__":
    backup_outputs()

