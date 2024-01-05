import os
import traceback
import pyspark
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import from_json, col, current_timestamp, window, expr
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    IntegerType,
)

import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement


os.environ["PYSPARK_PYTHON"] = "python3"
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"

# cluster = Cluster(
#     ["cassandra-node"]
# )  # Thay '172.18.0.2' bằng địa chỉ IP của máy chủ Cassandra


def send_data(tags: dict) -> None:
    url = "http://localhost:5001/updateData"
    response = requests.post(url, json=tags)


def process_row(row: pyspark.sql.types.Row) -> None:
    # print(type(row))  # pyspark.sql.types.Row
    # print(row)            # Row(hashtag='#BSCGems', count=2)
    tags = row.asDict()
    print(tags)  # {'hashtag': '#Colorado', 'count': 1}
    # send_data(tags)


def sourceCount(time):
    spark = SparkSession.builder.appName("KafkaSparkStreaming").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "localhost:29092")
        .option("subscribe", "news")
        .load()
    )
    lines = df.selectExpr("CAST(value AS STRING)")
    # df_parsed = df.selectExpr("CAST(value AS STRING)", "timestamp(crawled_at) as timestamp")
    schema = StructType(
        [
            StructField("id", StringType()),
            StructField("author", StringType()),
            StructField("content", StringType()),
            StructField("picture_count", IntegerType()),
            StructField("processed", IntegerType()),
            StructField("source", StringType()),
            StructField("title", StringType()),
            StructField("topic", StringType()),
            StructField("url", StringType()),
            StructField("crawled_at", TimestampType()),
        ]
    )
    df_parsed = df.select(from_json(col("value").cast("string"), schema).alias("data"))
    # Trích xuất các trường từ JSON và thêm trường 'time_received'
    df_extracted = df_parsed.select(
        "data.*", current_timestamp().alias("time_received")
    )

    # df_info = df.select("id", "source", "title", "url")
    # df_info.write \
    #     .csv('doc_info.csv', mode='overwrite')

    # session = cluster.connect(
    #     "topic_keyspace"
    # )  # Thay 'Topic_keyspace' bằng tên keyspace của bạn
    # # Drop bảng nếu tồn tại
    # # drop_table_query = "DROP TABLE IF EXISTS topic_table;"
    # # session.execute(drop_table_query)
    # # Tạo bảng nếu chưa tồn tại
    # create_table_query = """
    #     CREATE TABLE IF NOT EXISTS topic_table (
    #         source TEXT,
    #         window TIMESTAMP,
    #         count INT,
    #     );
    # """
    # session.execute(create_table_query)
    # # Đẩy dữ liệu vào bảng Cassandra
    # for _, row in df.iterrows():
    #     row = row.fillna("")
    #     insert_query = """
    #             INSERT INTO topic_table (
    #                 id, source, title, url
    #             )
    #             VALUES (%s, %s, %s, %s, %s);
    #         """
    #     session.execute(
    #         SimpleStatement(insert_query),
    #         (
    #             row["id"],
    #             row["source"],
    #             row["title"],
    #             row["url"]
    #         ),
    #     )

    # # Đóng kết nối
    # cluster.shutdown()

    article_counts = df_extracted.groupBy(
        window(col("time_received"), f"{time} seconds"), col("source")
    ).count()

    # Viết kết quả ra console, trigger mỗi 20 giây
    query = (
        article_counts.writeStream.outputMode("update")
        .format("console")
        .trigger(processingTime=f"{time} seconds")
        .start()
    )
    query.awaitTermination()
    print()

    query.write.csv("topic_doc1.csv", mode="overwrite")

    # df = pd.read_csv("topic_doc1.csv", header=0)  # Assuming the header is in the first row

    # # Kết nối đến Cassandra
    # session = cluster.connect(
    #     "topic_keyspace"
    # )  # Thay 'Topic_keyspace' bằng tên keyspace của bạn
    # # Drop bảng nếu tồn tại
    # drop_table_query = "DROP TABLE IF EXISTS source_table;"
    # session.execute(drop_table_query)
    # # Tạo bảng nếu chưa tồn tại
    # create_table_query = """
    #     CREATE TABLE IF NOT EXISTS source_table (
    #         source TEXT,
    #         window TIMESTAMP,
    #         count INT,
    #     );
    # """
    # session.execute(create_table_query)
    # # Đẩy dữ liệu vào bảng Cassandra
    # for _, row in df.iterrows():
    #     row = row.fillna("")
    #     insert_query = """
    #             INSERT INTO source_table (
    #                 window, source, count
    #             )
    #             VALUES (%s, %s, %s);
    #         """
    #     session.execute(
    #         SimpleStatement(insert_query),
    #         (
    #             row["window"],
    #             row["source"],
    #             row["count"],
    #         ),
    #     )

    # # Đóng kết nối
    # cluster.shutdown()


# Trích xuất các trường từ JSON


# # Nhóm và đếm theo nguồn
#     source_counts = df_extracted.groupBy("source").count()

# # Viết kết quả ra console
#     query = source_counts.writeStream \
#         .outputMode("complete") \
#         .format("console") \
#         .start()

#     query.awaitTermination()


# words = lines.select(explode(split(lines.value, " ")).alias("hashtag"))
# wordCounts = words.groupBy("hashtag").count()


# query2 = wordCounts.writeStream.foreach(process_row).outputMode('update').start()
# query2.awaitTermination()


if __name__ == "__main__":
    try:
        sourceCount(20)
    except BrokenPipeError:
        exit("Pipe Broken, Exiting...")
    except KeyboardInterrupt:
        exit("Keyboard Interrupt, Exiting..")
    except Exception as e:
        traceback.print_exc()
        exit("Error in Spark App")

# id, author, content, source, topic, url, crawled_at
