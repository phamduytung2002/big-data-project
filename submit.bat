cls
echo hello
export PYSPARK_PYTHON=/usr/bin/python3

docker cp submit.py spark-master:submit.py
@REM docker exec spark-master python3 ../submit.py
docker exec spark-master /spark/bin/spark-submit submit.py

@REM docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec spark-master /spark/bin/spark-submit consumer.py