cls
echo hello
docker cp model.py spark-master:model.py
@REM docker exec spark-master python3 ../model.py
docker exec spark-master /spark/bin/spark-submit --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.2.0 model.py 

@REM docker cp consumer/consumer.py spark-master:consumer.py
@REM docker exec spark-master /spark/bin/spark-submit consumer.py