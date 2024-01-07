Start cmd "conda activate bigdata & python news-producer/producer.py"

timeout /t 6 

docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec -it spark-master python3 ../consumer.py
docker exec -it spark-master /spark/bin/spark-submit  --executor-memory 500m --total-executor-cores 3 --master spark://spark-master:7077 consumer.py
