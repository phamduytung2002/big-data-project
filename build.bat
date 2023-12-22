docker-compose down
docker-compose up -d
docker exec -it namenode hadoop dfsadmin -safemode leave
docker exec -it namenode hadoop dfs -rm -r /user
docker exec -it namenode hdfs dfs -ls /

docker exec -it spark-master apk update
docker exec -it spark-master python3 -m pip install --upgrade pip
docker exec -it spark-master apk add --no-cache python3-dev py3-pip build-base
docker exec -it spark-master apk add --no-cache lapack-dev libexecinfo-dev
docker exec -it spark-master apk add build-base python3-dev
docker exec -it spark-master python3 -m ensurepip --default-pip
docker exec -it spark-master wget https://bootstrap.pypa.io/get-pip.py get-pip.py
docker exec -it spark-master python3 get-pip.py
docker exec -it spark-master pip install --upgrade pip setuptools
docker exec -it spark-master pip3 install numpy --compile --pre
docker exec -it spark-master pip3 install sparknlp
docker exec -it spark-master pip3 install kafka-python
docker exec -it spark-master pip3 install hdfs
docker exec spark-master apk add gfortran
@REM docker exec -it spark-master spark/bin/spark-shell --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.2.0
@REM docker exec spark-master export CC=gcc
@REM docker exec spark-master export CXX=g++
@REM docker exec -it spark-master pip3 install underthesea
