# executed within container
import sys
import os

from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("") \
    .master("spark://localhost:7077") \
    .config("spark.sql.caseSensitive", True) \
    .getOrCreate()

parquetFile = spark.read.parquet(sys.argv[2])
parquetFile.createOrReplaceTempView("parquetFile")

results = spark.sql(f"SELECT * FROM parquetFile WHERE {sys.argv[1]};")
print(results.count())

