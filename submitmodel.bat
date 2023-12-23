cls
echo hello
docker cp model.py spark-master:model.py
@REM docker exec spark-master python3 ../model.py
docker exec spark-master /spark/bin/spark-submit --master spark://spark-master:7077 --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0,commons-configuration:commons-configuration:1.10,com.github.jnr:jnr-posix:3.1.18 model.py 

@REM docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec spark-master /spark/bin/spark-submit consumer.py