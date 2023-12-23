import sys
import os

print("python version: ", sys.version)

from sparknlp.base import *
from sparknlp.annotator import *
import sparknlp
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf
import pyspark
import socket
from pyspark.sql.functions import col, array_position, array_max
from pyspark.sql.types import DoubleType, IntegerType

import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement


import csv

# Sample data
data = [
    ["id", "topic"],
    ["0", 0],
    ["1", 1],
    ["2", 2],
]

# Specify the file path
csv_file_path = "topic_doc2.csv"

# Writing to CSV file
with open(csv_file_path, mode="w", newline="") as file:
    writer = csv.writer(file)

    # Write the header
    writer.writerow(data[0])

    # Write the data rows
    writer.writerows(data[1:])

print(f"Data has been written to {csv_file_path}")

# send to cassandra

# host = "cassandra-node"
# port = 10000

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Connecting with Server
# sock.connect((host, port))

# while True:
#     filename = "topic_doc2.csv"
#     try:
#         # Reading file and sending data to server
#         fi = open(filename, "r")
#         data = fi.read()
#         if not data:
#             break
#         while data:
#             sock.send(str(data).encode())
#             data = fi.read()
#             # File is closed after data is sent
#             fi.close()

#     except IOError:
#         print("You entered an invalid filename!")


df = pd.read_csv("topic_doc2.csv", header=0)  # Assuming the header is in the first row

# Kết nối đến Cassandra
cluster = Cluster(
    ["cassandra-node"]
)  # Thay '172.18.0.2' bằng địa chỉ IP của máy chủ Cassandra
session = cluster.connect(
    "topic_keyspace"
)  # Thay 'Topic_keyspace' bằng tên keyspace của bạn
# Drop bảng nếu tồn tại
drop_table_query = "DROP TABLE IF EXISTS topic_table;"
session.execute(drop_table_query)
# Tạo bảng nếu chưa tồn tại
create_table_query = """
    CREATE TABLE IF NOT EXISTS topic_table (
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
for _, row in df.iterrows():
    row = row.fillna("")
    insert_query = """
            INSERT INTO topic_table (
                id, topic
            )
            VALUES (%s, %s);
        """
    session.execute(
        SimpleStatement(insert_query),
        (
            row["id"],
            row["topic"],
        ),
    )

# Đóng kết nối
cluster.shutdown()

exit()


# Define a UDF to find the argmax
@udf(IntegerType())
def argmax_udf(v):
    return int(v.argmax())


print("spark version: ", pyspark.__version__)
print("sparknlp version: ", sparknlp.version())
# from underthesea import word_tokenize

# tok = udf(lambda x: word_tokenize(x) if x is not None else None)

keyspace_name = "batch_process"
table_name = "all"


spark = (
    SparkSession.builder.appName("Spark NLP")
    .config("spark.driver.memory", "8G")
    .config("spark.driver.maxResultSize", "2G")
    .config("spark.kryoserializer.buffer.max", "1000M")
    .config("spark.dse.continuousPagingEnabled", "false")
    .config("spark.sql.hive.enabled", "false")
    .getOrCreate()
)

print("python version: ", sys.version)
print("spark version: ", pyspark.__version__)
print("spark nlp version: ", sparknlp.version())

# exit()

file_location = r"hdfs://namenode:9000/user/pdt/news/new_batch.csv"
file_type = "csv"
# CSV options
infer_schema = "true"
first_row_is_header = "true"
delimiter = "|||"
df = (
    spark.read.format(file_type)
    .option("inferSchema", infer_schema)
    .option("header", first_row_is_header)
    .option("sep", delimiter)
    .load(file_location)
)
# Verify the count
print("numnber of rows:")
print(df.count())
# Verify the schema
print("Schema:")
# df = df.withColumn('content_tokenized', tok(col('content')))
df.printSchema()
df.show()

print("python version: ", sys.version)
print("spark version: ", pyspark.__version__)
print("spark nlp version: ", sparknlp.version())

# overthesea_tokenize_udf = udf(tok, StringType())
# df = df.withColumn('abc', overthesea_tokenize_udf(col('author')))
# df.show()


# Spark NLP requires the input dataframe or column to be converted to document.
document_assembler = (
    DocumentAssembler()
    .setInputCol("content")
    .setOutputCol("document")
    .setCleanupMode("shrink")
)
# Split sentence to tokens(array)
tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("token")
# clean unwanted characters and garbage
normalizer = Normalizer().setInputCols(["token"]).setOutputCol("normalized")
# remove stopwords
# stopwords_cleaner = StopWordsCleaner.pretrained() \
#      .setInputCols("normalized")\
#      .setOutputCol("cleanTokens")\
#      .setCaseSensitive(False)
# stem the words to bring them to the root form.
stemmer = Stemmer().setInputCols(["normalized"]).setOutputCol("stem")
# Finisher is the most important annotator. Spark NLP adds its own structure when we convert each row in the dataframe to document. Finisher helps us to bring back the expected structure viz. array of tokens.
finisher = (
    Finisher()
    .setInputCols(["stem"])
    .setOutputCols(["tokens"])
    .setOutputAsArray(True)
    .setCleanAnnotations(False)
)
# We build a ml pipeline so that each phase can be executed in sequence. This pipeline can also be used to test the model.
nlp_pipeline = Pipeline(
    stages=[
        document_assembler,
        tokenizer,
        normalizer,
        # stopwords_cleaner,
        stemmer,
        finisher,
    ]
)
# train the pipeline
nlp_model = nlp_pipeline.fit(df)
# apply the pipeline to transform dataframe.
processed_df = nlp_model.transform(df)
# nlp pipeline create intermediary columns that we dont need. So lets select the columns that we need
tokens_df = processed_df.select("id", "author", "tokens").limit(5)
tokens_df.show()

from pyspark.ml.feature import CountVectorizer

cv = CountVectorizer(inputCol="tokens", outputCol="features", vocabSize=500, minDF=3.0)
# train the model
cv_model = cv.fit(tokens_df)
# transform the data. Output column name will be features.
vectorized_tokens = cv_model.transform(tokens_df)
vectorized_tokens.show()

from pyspark.ml.clustering import LDA

num_topics = 5
lda = LDA(k=num_topics, optimizer="em")
model = lda.fit(vectorized_tokens)
model.getTopicDistributionCol()
ll = model.logLikelihood(vectorized_tokens)
lp = model.logPerplexity(vectorized_tokens)
print("The lower bound on the log likelihood of the entire corpus: " + str(ll))
print("The upper bound on perplexity: " + str(lp))
model.transform(vectorized_tokens).printSchema()

df_transformed = model.transform(vectorized_tokens).withColumn(
    "topic", argmax_udf("topicDistribution")
)

doc_topic_dist = df_transformed.select("id", "topic")


doc_topic_dist.write.csv("topic_doc2.csv", header=True, mode="overwrite")


# send to cassandra

host = "cassandra-node"
port = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connecting with Server
sock.connect((host, port))

while True:
    filename = "topic_doc2.csv"
    try:
        # Reading file and sending data to server
        fi = open(filename, "r")
        data = fi.read()
        if not data:
            break
        while data:
            sock.send(str(data).encode())
            data = fi.read()
            # File is closed after data is sent
            fi.close()

    except IOError:
        print("You entered an invalid filename!")


## extract vocabulary from CountVectorizer
# vocab = cv_model.vocabulary
# topics = model.describeTopics()
# topics_rdd = topics.rdd
# topics_words = topics_rdd\
#       .map(lambda row: row['termIndices'])\
#       .map(lambda idx_list: [vocab[idx] for idx in idx_list])\
#       .collect()
# for idx, topic in enumerate(topics_words):
#    print("topic: {}".format(idx))
#    print("*"*25)
#    for word in topic:
#       print(word)
#    print("*"*25)

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Connecting with Server
# sock.connect(('cassandra-node', 10000))

spark.stop()
