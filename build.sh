sudo docker-compose down
sudo docker-compose up -d
sudo docker exec -it namenode hadoop dfsadmin -safemode leave
sudo docker exec -it namenode hadoop dfs -rm -r /user
sudo docker exec -it namenode hdfs dfs -ls /

sudo docker exec -it spark-master apk update
sudo docker exec -it spark-master python3 -m pip install --upgrade pip
sudo docker exec -it spark-master apk add --no-cache python3-dev py3-pip build-base
sudo docker exec -it spark-master apk add --no-cache lapack-dev libexecinfo-dev
sudo docker exec -it spark-master apk add build-base python3-dev
sudo docker exec -it spark-master python3 -m ensurepip --default-pip
sudo docker exec -it spark-master wget https://bootstrap.pypa.io/get-pip.py get-pip.py
sudo docker exec -it spark-master python3 get-pip.py
sudo docker exec -it spark-master pip install --upgrade pip setuptools
sudo docker exec -it spark-master pip3 install numpy --compile --pre
sudo docker exec -it spark-master pip3 install sparknlp
sudo docker exec -it spark-master pip3 install kafka-python
sudo docker exec -it spark-master pip3 install hdfs
sudo docker exec -it spark-master pip3 install pandas
sudo docker exec -it spark-master pip3 install cassandra-driver
sudo docker exec spark-master apk add gfortran
@REM sudo docker exec -it spark-master spark/bin/spark-shell --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.2.0
@REM sudo docker exec spark-master export CC=gcc
@REM sudo docker exec spark-master export CXX=g++
@REM sudo docker exec -it spark-master pip3 install underthesea
