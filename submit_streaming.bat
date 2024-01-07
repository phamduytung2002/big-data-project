docker cp streaming.py spark-master:/streaming.py
docker exec -it spark-master /spark/bin/spark-submit --total-executor-cores 1 --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 streaming.py