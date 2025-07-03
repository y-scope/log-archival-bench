# executed within container
import sys

from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("") \
    .master("local[1]") \
    .config("spark.sql.caseSensitive", True) \
    .getOrCreate()
    #.config("spark.io.compression.zstd.level", "3") \

df = spark.read.json(sys.argv[1])
df.write.parquet(sys.argv[2], mode="overwrite", compression="zstd")  # need to set zstd(3)
