Start "" python news-producer/producer.py 

timeout /t 6 

docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec -it spark-master python3 ../consumer.py
docker exec -it spark-master /spark/bin/spark-submit consumer.py
