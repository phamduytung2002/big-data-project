import os
import traceback
import pyspark
import requests
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import from_json, col, current_timestamp, window, expr
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType

import threading
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.policies import ReconnectionPolicy

def save_to_cassandra(rdd):
    if not rdd.isEmpty():
        rdd.saveToCassandra("your_keyspace", "your_table")


os.environ["PYSPARK_PYTHON"] = "python3"
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"

def send_data(tags: dict) -> None:
    # url = 'http://localhost:5001/updateData'
    # response = requests.post(url, json=tags)
    print(tags)


class CustomReconnectionPolicy(ReconnectionPolicy):
    def new_schedule(self):
        # Reconnect every 5 seconds
        return [5]
    

def sourceCount(time):
    spark = SparkSession.builder.appName("KafkaSparkStreaming").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-1:9092") \
        .option("subscribe", "newsss") \
        .load()
    # df_parsed = df.selectExpr("CAST(value AS STRING)", "timestamp(crawled_at) as timestamp")
    schema = StructType([
    StructField("id", StringType()),
    StructField("author", StringType()),
    StructField("content", StringType()),
    StructField("picture_count", IntegerType()),
    StructField("processed",IntegerType()),
    StructField("source", StringType()),
    StructField("title", StringType()),
    StructField("topic", StringType()),
    StructField("url", StringType()),
    StructField("crawled_at", TimestampType())
])
    df_parsed = df.select(from_json(col("value").cast("string"), schema).alias("data"))
    # Trích xuất các trường từ JSON và thêm trường 'time_received'
    df_extracted = df_parsed.select(
        "data.*",
        current_timestamp().alias("time_received")
    )

    cluster = Cluster(
        ["cassandra-node"],
        connect_timeout=1000,
        connection_timeout=10,
        reconnection_policy=CustomReconnectionPolicy(),
    )  # Thay '172.18.0.2' bằng địa chỉ IP của máy chủ Cassandra

    session = cluster.connect(
        "newshub"
    )  
    
    def process_ori_thread(df, epoch_id):
        if not df.rdd.isEmpty():
            print(f"Batch {epoch_id} - Dữ liệu:")
            for row in df.toLocalIterator():
                print(row)
                # row = row.fillna("")
                insert_query = """
                    INSERT INTO article (
                        id, author, source, title, url
                    )
                    VALUES (%s, %s, %s, %s, %s);
                """
                session.execute(
                SimpleStatement(insert_query),
                (
                    int(row["id"]),
                    row["author"],
                    row["source"],
                    row["title"],
                    row["url"]
                ),
                )

        else:
            print(f"Batch {epoch_id} is empty")
            
    def process_ori(df, epoch_id):
        thread = threading.Thread(target=process_ori_thread, args=(df, epoch_id))
        thread.start()
    
    query = df_extracted.writeStream \
        .outputMode("update") \
        .foreachBatch(process_ori) \
        .trigger(processingTime=f"{time} seconds") \
        .start()
    # query.awaitTermination()


    article_counts = df_extracted.groupBy(
        window(col("time_received"), f"{time} seconds"),
        col("source")
    ).count()

    collected_data = []

    def process_row(df, epoch_id):
        if not df.rdd.isEmpty():
            print(f"Batch {epoch_id} - Dữ liệu:")
            # Drop bảng nếu tồn tại
            drop_table_query = "DROP TABLE IF EXISTS source_count;"
            session.execute(drop_table_query)
            # Tạo bảng nếu chưa tồn tại
            create_table_query = """
                CREATE TABLE IF NOT EXISTS source_count (
                    source TEXT PRIMARY KEY,
                    count INT,
                    window TIMESTAMP
                );
            """
            session.execute(create_table_query)
            for row in df.toLocalIterator():
                print(row)
                # row = row.fillna("")
                insert_query = """
                    INSERT INTO source_count (
                        source, count, window
                    )
                    VALUES (%s, %s, %s);
                """
                session.execute(
                SimpleStatement(insert_query),
                (
                    row["source"],
                    int(row["count"]),
                    row['window']['start']
                ),
                )

        else:
            print(f"Batch {epoch_id} is empty")

    query = article_counts.writeStream \
        .outputMode("update") \
        .foreachBatch(process_row) \
        .trigger(processingTime=f"{time} seconds") \
        .start()
    query.awaitTermination()


    return collected_data

if __name__ == '__main__':
    while True:
        try:
            collected_source_counts = sourceCount(50)
            for data in collected_source_counts:
                print('hello')
        except BrokenPipeError:
            exit("Pipe Broken, Exiting...")
        except KeyboardInterrupt:
            exit("Keyboard Interrupt, Exiting..")
        except Exception as e:
            traceback.print_exc()
            exit("Error in Spark App")

#id, author, content, source, topic, url, crawled_at