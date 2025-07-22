#!/usr/bin/env python3

import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
import sys
from openpyxl.utils import get_column_letter
import collections
# Get the current working directory
current_dir = os.getcwd()

# Add it to sys.path
if current_dir not in sys.path:
    sys.path.append(current_dir)

def prettify_json(to_prettify, ignore=[]):
    return ', '.join([f"{key}={val}" for key, val in json.loads(to_prettify).items() if key not in ignore])

current_dir = Path(os.getcwd())
parent_dir = Path(os.path.realpath(__file__)).parent.parent

if current_dir != parent_dir:
    raise Exception(f"Script can only be run in {parent_dir}")

from src.jsonsync import JsonItem

def avg(data_original):
    data = [i for i in data_original if i > 0]
    if not data:
        return 0
    else:
        return sum(data) / len(data)

dataset_sizes = {
        'mongod': 69582861765,
        'elasticsearch': 8565304619,
        'cockroachdb': 10506623721,
        'postgresql': 411917670,
        'spark-event-logs': 2126027157,
        }


assets_dir = current_dir / "assets"
outputs = [p for p in assets_dir.iterdir() if p.is_dir() if os.path.basename(str(p)) != "__pycache__"]

outsheet = JsonItem([])
outsheet[2][0] = 'target'
outsheet[2][1] = 'target-display-name'
outsheet[2][2] = 'type'
outsheet[2][3] = 'color'

dataset_y = {}
y = 4
for dataset in dataset_sizes.keys():
    dataset_y[dataset] = y
    for field in ('Ingestion time (ms)', 'Compressed size (B)', 'Ingestion memory usage (B)', 'Size (B)', 'Compression Ratio', 'Ingestion Speed (MB/s)'):
        outsheet[0][y] = dataset
        outsheet[2][y] = field
        y += 1
    y += 1

averages_y = y
for field in ('Ingestion time (ms)', 'Ingestion memory usage (B)', 'Compression Ratio', 'Ingestion Speed (MB/s)'):
    outsheet[0][y] = 'Average'
    outsheet[2][y] = field
    y += 1

query_y = {}
for temp in ('cold', 'hot'):
    y += 1
    query_y[temp] = y
    for i in range(6):
        outsheet[0][y] = 'mongod'
        outsheet[1][y] = temp
        outsheet[2][y] = f"Q{i} time (ms)"
        y += 1
    outsheet[0][y] = 'mongod'
    outsheet[1][y] = temp
    outsheet[2][y] = 'Query memory usage (B)'
    y += 1


columns = {}

# to average
ingestion_time = collections.defaultdict(list)
ingestion_memory = collections.defaultdict(list)
compression_ratio = collections.defaultdict(list)
ingestion_speed = collections.defaultdict(list)

for output_dir in outputs:
    tool = os.path.basename(output_dir.resolve())
    filename = (output_dir / "output.json").resolve()
    if not os.path.exists(str(filename)):
        continue
    with open(filename, 'r') as file:
        output = json.load(file)
        for dataset, dataset_val in output.items():
            for configuration, configuration_val in dataset_val.items():
                # multiple iterations write to the same column
                
                title = f"{tool} ({prettify_json(configuration, ['timestamp', 'dataset_variation', 'keys', 'order_by'])})"
                if title not in columns:
                    column = JsonItem([])
                    columns[title] = column
                else:
                    column = columns[title]

                column[0] = title  # target
                # target-display name
                column[2] = 2  # type
                # color

                compressed_size = None
                uncompressed_size = None
                time_taken = None
                for key, value in configuration_val["ingest"].items():
                    if key == "memory_average_B":
                        column[dataset_y[dataset] + 2] = value # ingestion memory usage (B)
                        ingestion_memory[title].append(value)
                    elif key == "compressed_size_B":
                        compressed_size = value
                        column[dataset_y[dataset] + 1] = value # compressed size (B)
                    elif key == "decompressed_size_B":
                        uncompressed_size = value
                        column[dataset_y[dataset] + 3] = value # size (B)
                    elif key == "time_taken_s":
                        time_taken = value
                        column[dataset_y[dataset] + 0] = value * 1000 # ingestion time (ms)
                        ingestion_time[title].append(value * 1000)

                if compressed_size is not None and uncompressed_size is not None and compressed_size != 0:
                    column[dataset_y[dataset] + 4] = uncompressed_size / compressed_size  # Compression Ratio
                    compression_ratio[title].append(uncompressed_size / compressed_size)

                if uncompressed_size is not None  and time_taken is not None and time_taken != 0:
                    column[dataset_y[dataset] + 5] = uncompressed_size / time_taken / 1024 / 1024 # Ingestion Speed (MB/s)
                    ingestion_speed[title].append(uncompressed_size / time_taken / 1024 / 1024 )

                # only one set of queries in the same configuration_val iteration, so we can do this
                memory_cold = []
                memory_hot = []
                if "query_cold" in configuration_val and "query_hot" in configuration_val:
                    for key, value in enumerate(configuration_val["query_cold"]):
                        column[query_y['cold'] + key] = value["time_taken_s"] * 1000 # Qx time (ms) (cold)
                        if value["memory_average_B"] != -1:
                            memory_cold.append(value["memory_average_B"])

                    for key, value in enumerate(configuration_val["query_hot"]):
                        column[query_y['hot'] + key] = value["time_taken_s"] * 1000 # Qx time (ms) (hot)
                        if value["memory_average_B"] != -1:
                            memory_hot.append(value["memory_average_B"])

                if memory_cold:
                    memory_cold_val = sum(memory_cold)/len(memory_cold)
                    column[query_y['cold'] + 6] = memory_cold_val  # Query memory usage (B)

                if memory_hot:
                    memory_hot_val = (sum(memory_hot)/len(memory_hot))
                    column[query_y['hot'] + 6] = memory_hot_val  # Query memory usage (B)


                column[averages_y] = avg(ingestion_time[title])
                column[averages_y + 1] = avg(ingestion_memory[title])
                column[averages_y + 2] = avg(compression_ratio[title])
                column[averages_y + 3] = avg(ingestion_speed[title])

x = 3
for column in columns.values():
    outsheet[x] = column
    x += 1


sheet_name = 'UI Input Format'
data = outsheet

df = pd.DataFrame(data.compile()).T

df.to_excel("clp_bench_abby.xlsx", sheet_name=sheet_name)
