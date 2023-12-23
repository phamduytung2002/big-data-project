clear

sudo docker cp submit.py spark-master:submit.py
@REM sudo docker exec spark-master python3 ../submit.py
sudo docker exec spark-master /spark/bin/spark-submit --master spark://spark-master:7077 submit.py

@REM sudo docker cp consumer/consumer.py spark-master:consumer.py
@REM sudo docker exec spark-master /spark/bin/spark-submit consumer.py