docker cp E:\big-data-project\submit.py spark-master:submit.py
docker exec spark-master /spark/bin/spark-submit --master spark://spark-master:7077 submit.py

docker cp E:\big-data-project\model.py spark-master:model.py
docker exec spark-master /spark/bin/spark-submit --master spark://spark-master:7077 --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.2.0 model.py 
