import pyarrow as pa
import pyarrow.parquet as pq
import json
import sys
import time

sys.setrecursionlimit(1000)

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = "/home/hive-data/bench_schema/bench_table/mongod.parquet"
#OUTPUT_FILE = "mongod.parquet"
BATCH_SIZE = 1000

def extract_fields_and_values(obj, prefix=""):
    result = {
        "string": {"columns": [], "values": []},
        "int": {"columns": [], "values": []},
        "float": {"columns": [], "values": []},
        "bool": {"columns": [], "values": []}
    }

    def recurse(sub_obj, current_path):
        if isinstance(sub_obj, dict):
            for k, v in sub_obj.items():
                new_path = f"{current_path}.{k}" if current_path else k
                assert sub_obj != v
                recurse(v, new_path)
        elif isinstance(sub_obj, list):
            for i, item in enumerate(sub_obj):
                new_path = f"{current_path}[{i}]"
                recurse(item, new_path)
        else:
            if isinstance(sub_obj, str):
                typ = "string"
            elif isinstance(sub_obj, bool):
                typ = "bool"
            elif isinstance(sub_obj, int):
                typ = "int"
            elif isinstance(sub_obj, float):
                typ = "float"
            else:
                return  # skip unknown types
            result[typ]["columns"].append(current_path)
            result[typ]["values"].append(sub_obj)

    recurse(obj, prefix)
    return result

# Define schema for Parquet
schema = pa.schema([
    ("string_columns", pa.list_(pa.string())),
    ("string_values", pa.list_(pa.string())),
    ("int_columns", pa.list_(pa.string())),
    ("int_values", pa.list_(pa.int64())),
    ("float_columns", pa.list_(pa.string())),
    ("float_values", pa.list_(pa.float64())),
    ("bool_columns", pa.list_(pa.string())),
    ("bool_values", pa.list_(pa.bool_())),
])

batch = {}

def resetbatch():
    global batch
    batch = {
                "string_columns": [],
                "string_values": [],
                "int_columns": [],
                "int_values": [],
                "float_columns": [],
                "float_values": [],
                "bool_columns": [],
                "bool_values": [],
            }

resetbatch()

with pq.ParquetWriter(OUTPUT_FILE, schema, compression="ZSTD", compression_level=3) as writer:
#with pq.ParquetWriter(OUTPUT_FILE, schema) as writer:
    with open(INPUT_FILE, "r") as f:
        i = 0
        for line in f:
            if (line == '\n' or not line):
                continue

            i += 1

            data = json.loads(line)
            extracted = extract_fields_and_values(data)

            batch["string_columns"].append(extracted["string"]["columns"])
            batch["string_values"].append(extracted["string"]["values"])
            batch["int_columns"].append(extracted["int"]["columns"])
            batch["int_values"].append(extracted["int"]["values"])
            batch["float_columns"].append(extracted["float"]["columns"])
            batch["float_values"].append(extracted["float"]["values"])
            batch["bool_columns"].append(extracted["bool"]["columns"])
            batch["bool_values"].append(extracted["bool"]["values"])

            # Write a batch every N lines
            if i % BATCH_SIZE == 0:
                print(i)
                table = pa.table(batch, schema=schema)
                writer.write_table(table)
                resetbatch()
        # Write remaining lines
        if batch:
            table = pa.table(batch, schema=schema)
            writer.write_table(table)

