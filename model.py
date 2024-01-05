import sys
import os
import numpy as np
from sparknlp.base import *
import time
from sparknlp.annotator import *
import sparknlp
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf
import pyspark
import socket
import pyspark.sql.functions as F
from pyspark.sql.functions import col, array_position, array_max
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.ml.functions import vector_to_array
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from pyspark.ml.linalg import VectorUDT
import csv
from pyspark.sql.functions import udf
from pyspark.ml import Pipeline
from pyspark.ml.feature import SQLTransformer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.clustering import LDA


spark = (
    SparkSession.builder.appName("Spark NLP")
    .config("spark.driver.memory", "8G")
    .config("spark.driver.maxResultSize", "2G")
    .config("spark.kryoserializer.buffer.max", "1000M")
    .config("spark.dse.continuousPagingEnabled", "false")
    .config("spark.sql.hive.enabled", "false")
    .config("user.home", "/")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# check version
print("python version: ", sys.version)
print("spark version: ", pyspark.__version__)
print("spark nlp version: ", sparknlp.version())

# read file from hdfs
file_location = r"hdfs://namenode:9000/user/pdt/news/new_batch.csv"
file_type = "csv"
# CSV options
infer_schema = "true"
first_row_is_header = "true"
delimiter = "|"
df = (
    spark.read.format(file_type)
    .option("inferSchema", infer_schema)
    .option("header", first_row_is_header)
    .option("sep", delimiter)
    .load(file_location)
    .repartition(2)
)

# concatenate title, content and topic
concatStage = SQLTransformer(
    statement="""
    SELECT
        *, 
        CONCAT(`title`, ' ', COALESCE(content, ''), ' ', topic) AS concat
    FROM __THIS__;
    """
)


# build sparknlp preprocessing pipeline
document_assembler = (
    DocumentAssembler()
    .setInputCol("concat")
    .setOutputCol("document")
    .setCleanupMode("shrink")
)
tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("token")
normalizer = Normalizer().setInputCols(["token"]).setOutputCol("normalized")
# stopwords_cleaner = StopWordsCleaner.pretrained() \
#      .setInputCols("normalized")\
#      .setOutputCol("cleanTokens")\
#      .setCaseSensitive(False)
# Finisher is the most important annotator. Spark NLP adds its own structure when we convert each row in the dataframe to document. Finisher helps us to bring back the expected structure viz. array of tokens.
finisher = (
    Finisher()
    .setInputCols(["normalized"])
    .setOutputCols(["tokens"])
    .setOutputAsArray(True)
    .setCleanAnnotations(False)
)

cv = CountVectorizer(inputCol="tokens", outputCol="features", vocabSize=500, minDF=3.0)

num_topics = 5
lda = LDA(k=num_topics, optimizer="online", maxIter=1000)
lda.setCheckpointInterval(5)

argmax = spark.udf.register(
    "argmax", lambda x: int(np.argmax(x)), returnType=IntegerType()
)

ArgMaxStage = SQLTransformer(
    statement="SELECT *, int(argmax(topicDistribution)) as topic_lda FROM __THIS__"
)


nlp_pipeline = Pipeline(
    stages=[
        concatStage,
        document_assembler,
        tokenizer,
        normalizer,
        # stopwords_cleaner,
        finisher,
        cv,
        lda,
        ArgMaxStage,
    ]
)

nlp_model = nlp_pipeline.fit(df)
processed_df = nlp_model.transform(df)
# processed_df.show()
topic_lda_df = processed_df.select("id", "title", col("topic_lda").astype("int")).where(col('title').isNotNull())
# topic_lda_df.show()

topic_lda_pd_df = topic_lda_df.toPandas()

topic_lda_df.show()

# topic_lda_df.write.format("org.apache.spark.sql.cassandra").options(table="article", keyspace="newshub").save(mode="append")

# time.sleep(10000000)
spark.stop()

# exit()
# Kết nối đến Cassandra
cluster = Cluster(
    ["cassandra-node"]
)  # Thay '172.18.0.2' bằng địa chỉ IP của máy chủ Cassandra

session = cluster.connect(
    "newshub"
)  # Thay 'Topic_keyspace' bằng tên keyspace của bạn
# Drop bảng nếu tồn tại
# drop_table_query = "DROP TABLE IF EXISTS article;"
# session.execute(drop_table_query)
# Tạo bảng nếu chưa tồn tại
create_table_query = """
    CREATE TABLE IF NOT EXISTS article (
        id INT PRIMARY KEY,
        source TEXT,
        title TEXT,
        url TEXT,
        topic INT,
        crawled_at TEXT
    );
"""
session.execute(create_table_query)
# Đẩy dữ liệu vào bảng Cassandra
for _, row in topic_lda_pd_df.iterrows():
    row = row.fillna("")
    insert_query = """
            INSERT INTO article (
                id, topic
            )
            VALUES (%s, %s);
        """
    session.execute(
        SimpleStatement(insert_query),
        (
            int(row["id"]),
            int(row["topic_lda"]),
        ),
    )

# Đóng kết nối
cluster.shutdown()
