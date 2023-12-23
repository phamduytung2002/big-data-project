gnome-terminal --sh -c "python news-producer/producer.py" 


sudo docker cp consumer/consumer.py spark-master:consumer.py
sudo docker exec -it spark-master /spark/bin/spark-submit --master spark://spark-master:7077 consumer.py
