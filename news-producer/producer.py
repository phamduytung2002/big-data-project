import json
import time
import os
from kafka import KafkaProducer
import pprint

# Kafka broker address
bootstrap_servers = "localhost:29092"

# Kafka topic to publish to
kafka_topic = "news"

# Read JSON data from the file
data_source_path = os.path.join(os.path.dirname(__file__), "news_dataset.json")
with open(data_source_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

# Kafka producer configuration
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


# Function to publish an article to Kafka topic
def publish_article(article):
    key = str(article["id"]).encode("utf-8")  # Encode the key to bytes
    value = json.dumps(article).encode("utf-8")
    producer.send(kafka_topic, key=key, value=value)
    producer.flush()
    print("article sent")


# Publish an article every 5 seconds
for article in json_data:
    publish_article(article)
    time.sleep(2)

# Close the Kafka producer
producer.close()
