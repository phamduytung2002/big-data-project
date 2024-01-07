docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec -it spark-master python3 ../consumer.py
docker exec -it spark-master /spark/bin/spark-submit  --executor-memory 1G --total-executor-cores 2 --master spark://spark-master:7077 consumer.py
