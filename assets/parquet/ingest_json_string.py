import pyarrow as pa
import pyarrow.parquet as pq
import sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = "/home/hive-data/bench_schema/bench_table/output.parquet"
BATCH_SIZE = 10000

schema = pa.schema([("line", pa.string())])

#with pq.ParquetWriter(OUTPUT_FILE, schema) as writer:
with pq.ParquetWriter(OUTPUT_FILE, schema, compression="ZSTD", compression_level=3) as writer:
    batch = []
    with open(INPUT_FILE, "r") as f:
        for i, line in enumerate(f, 1):
            fullline = line.rstrip("\n")
            if not fullline:
                continue
            batch.append(fullline)
            # Write a batch every N lines
            if i % BATCH_SIZE == 0:
                table = pa.table({"line": batch}, schema=schema)
                writer.write_table(table)
                batch = []
        # Write remaining lines
        if batch:
            table = pa.table({"line": batch}, schema=schema)
            writer.write_table(table)

