import json
import time
import os
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
import pprint
import pandas
all_df = None

# Kafka broker address
bootstrap_servers = 'localhost:29092'
admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)


# Kafka topic to publish to
kafka_topic = 'newsss'
topic = NewTopic(name=kafka_topic, num_partitions=3, replication_factor=3)

# Read JSON data from the file
data_source_path = os.path.join(os.path.dirname(__file__), 'news_dataset.json')
with open(data_source_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    
try:
    admin_client.create_topics([topic])
except Exception as e:
    print(f"An unexpected error occurred: {e}")


# Kafka producer configuration
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Function to publish an article to Kafka topic
def publish_article(article):
    key = str(article["id"]).encode('utf-8')  # Encode the key to bytes
    value = json.dumps(article).encode('utf-8')
    producer.send(kafka_topic, key=key, value=value)
    producer.flush()
    print('article sent')
    global all_df
    for x in article:
        if isinstance(article[x], str):
            article[x] = article[x].replace('\n', ' ')
    if all_df is None:
        all_df = pandas.DataFrame([article])
    else:
        df = pandas.DataFrame([article])
        all_df = all_df._append(df, ignore_index=True)


# Publish an article every 5 seconds
for article in json_data:
    publish_article(article)
    time.sleep(0.5)

# Close the Kafka producer
producer.close()
