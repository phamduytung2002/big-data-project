# spark.read.option("header", "true").csv("hdfs://namenode:9000/user/pdt/news/2023_12_20_16_3_47_580002.csv").show()

import pyspark
import hdfs

base_path = "/user/pdt/news/"

client = hdfs.Client("http://namenode:9870")
files_list = client.list(base_path)

full_df = None

spark = pyspark.sql.SparkSession.builder.appName("xyz").getOrCreate()
for file_name in files_list:
    if full_df is None:
        full_df = spark.read \
            .option("delimiter","|||") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000" + base_path + file_name)
        full_df.write \
            .option("delimiter","|||") \
            .csv(f"hdfs://namenode:9000/user/pdt/processed/{file_name}", header=True)
    else:
        df = spark.read \
            .option("delimiter","|||") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000" + base_path + file_name)
        full_df = full_df.union(df)
        full_df.write \
            .option("delimiter","|||") \
            .csv(f"hdfs://namenode:9000/user/pdt/processed/{file_name}", header=True)


full_df.write \
    .option("delimiter", "|||") \
    .csv("hdfs://namenode:9000/user/pdt/news/new_batch.csv", header=True)

for file_name in files_list:
    client.delete(base_path + file_name, recursive=True)