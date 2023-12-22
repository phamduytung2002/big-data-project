import sys
import os
print('python version: ', sys.version)

from sparknlp.base import *
from sparknlp.annotator import *
import sparknlp
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf
import pyspark

print('spark version: ', pyspark.__version__)
print('sparknlp version: ', sparknlp.version())
# from underthesea import word_tokenize

# tok = udf(lambda x: word_tokenize(x) if x is not None else None)




spark = SparkSession.builder \
    .appName("Spark NLP") \
    .config("spark.driver.memory", "8G") \
    .config("spark.driver.maxResultSize", "2G") \
    .config("spark.kryoserializer.buffer.max", "1000M") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()


file_location = r'hdfs://namenode:9000/user/pdt/news/new_batch.csv'
file_type = "csv"
# CSV options
infer_schema = "true"
first_row_is_header = "true"
delimiter = "|||"
df = spark.read.format(file_type) \
 .option("inferSchema", infer_schema) \
 .option("header", first_row_is_header) \
 .option("sep", delimiter) \
 .load(file_location)
# Verify the count
print('numnber of rows:')
print(df.count())
# Verify the schema
print('Schema:')
# df = df.withColumn('content_tokenized', tok(col('content')))
df.printSchema()
df.show()

# overthesea_tokenize_udf = udf(tok, StringType())
# df = df.withColumn('abc', overthesea_tokenize_udf(col('author')))
# df.show()


# exit()


print('python version: ', sys.version)
print('spark version: ', pyspark.__version__)
print('spark nlp version: ', sparknlp.version())

# Spark NLP requires the input dataframe or column to be converted to document. 
document_assembler = DocumentAssembler() \
    .setInputCol("content") \
    .setOutputCol("document") \
    .setCleanupMode("shrink")
# Split sentence to tokens(array)
tokenizer = Tokenizer() \
    .setInputCols(["document"]) \
    .setOutputCol("token")
# clean unwanted characters and garbage
normalizer = Normalizer() \
    .setInputCols(["token"]) \
    .setOutputCol("normalized")
# remove stopwords
stopwords_cleaner = StopWordsCleaner.pretrained("stopwords_iso","vi") \
      .setInputCols("normalized")\
      .setOutputCol("cleanTokens")\
      .setCaseSensitive(False)
# stem the words to bring them to the root form.
stemmer = Stemmer() \
    .setInputCols(["cleanTokens"]) \
    .setOutputCol("stem")
# Finisher is the most important annotator. Spark NLP adds its own structure when we convert each row in the dataframe to document. Finisher helps us to bring back the expected structure viz. array of tokens.
finisher = Finisher() \
    .setInputCols(["stem"]) \
    .setOutputCols(["tokens"]) \
    .setOutputAsArray(True) \
    .setCleanAnnotations(False)
# We build a ml pipeline so that each phase can be executed in sequence. This pipeline can also be used to test the model. 
nlp_pipeline = Pipeline(
    stages=[document_assembler, 
            tokenizer,
            normalizer,
            stopwords_cleaner, 
            stemmer, 
            finisher])
# train the pipeline
nlp_model = nlp_pipeline.fit(df)
# apply the pipeline to transform dataframe.
processed_df  = nlp_model.transform(df)
# nlp pipeline create intermediary columns that we dont need. So lets select the columns that we need
tokens_df = processed_df.select('author','tokens').limit(5)
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
lda = LDA(k=num_topics,  )
model = lda.fit(vectorized_tokens)
model.getTopicDistributionCol()
print(model.topicsMatrix())
ll = model.logLikelihood(vectorized_tokens)
lp = model.logPerplexity(vectorized_tokens)
print("The lower bound on the log likelihood of the entire corpus: " + str(ll))
print("The upper bound on perplexity: " + str(lp))

model.transform(vectorized_tokens).select('tokens','topicDistribution').limit(1).show()

# extract vocabulary from CountVectorizer
vocab = cv_model.vocabulary
topics = model.describeTopics()   
topics_rdd = topics.rdd
topics_words = topics_rdd\
       .map(lambda row: row['termIndices'])\
       .map(lambda idx_list: [vocab[idx] for idx in idx_list])\
       .collect()
for idx, topic in enumerate(topics_words):
    print("topic: {}".format(idx))
    print("*"*25)
    for word in topic:
       print(word)
    print("*"*25)   

spark.stop()