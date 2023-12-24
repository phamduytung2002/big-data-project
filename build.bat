@REM docker-compose down
@REM docker-compose up -d
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
docker exec -it spark-master pip3 install pandas
docker exec -it spark-master pip3 install cassandra-driver
docker exec -it spark-master pip3 install vncorenlp



docker exec -it spark-worker-1 apk update
docker exec -it spark-worker-1 python3 -m pip install --upgrade pip
docker exec -it spark-worker-1 apk add --no-cache python3-dev py3-pip build-base
docker exec -it spark-worker-1 apk add --no-cache lapack-dev libexecinfo-dev
docker exec -it spark-worker-1 apk add build-base python3-dev
docker exec -it spark-worker-1 python3 -m ensurepip --default-pip
docker exec -it spark-worker-1 wget https://bootstrap.pypa.io/get-pip.py get-pip.py
docker exec -it spark-worker-1 python3 get-pip.py
docker exec -it spark-worker-1 pip install --upgrade pip setuptools
docker exec -it spark-worker-1 pip3 install numpy --compile --pre
docker exec -it spark-worker-1 pip3 install sparknlp
docker exec -it spark-worker-1 pip3 install kafka-python
docker exec -it spark-worker-1 pip3 install hdfs
docker exec spark-worker-1 apk add gfortran
docker exec -it spark-worker-1 pip3 install pandas
docker exec -it spark-worker-1 pip3 install cassandra-driver
docker exec -it spark-worker-1 pip3 install vncorenlp




docker exec -it spark-worker-2 apk update
docker exec -it spark-worker-2 python3 -m pip install --upgrade pip
docker exec -it spark-worker-2 apk add --no-cache python3-dev py3-pip build-base
docker exec -it spark-worker-2 apk add --no-cache lapack-dev libexecinfo-dev
docker exec -it spark-worker-2 apk add build-base python3-dev
docker exec -it spark-worker-2 python3 -m ensurepip --default-pip
docker exec -it spark-worker-2 wget https://bootstrap.pypa.io/get-pip.py get-pip.py
docker exec -it spark-worker-2 python3 get-pip.py
docker exec -it spark-worker-2 pip install --upgrade pip setuptools
docker exec -it spark-worker-2 pip3 install numpy --compile --pre
docker exec -it spark-worker-2 pip3 install sparknlp
docker exec -it spark-worker-2 pip3 install kafka-python
docker exec -it spark-worker-2 pip3 install hdfs
docker exec spark-worker-2 apk add gfortran
docker exec -it spark-worker-2 pip3 install pandas
docker exec -it spark-worker-2 pip3 install cassandra-driver
docker exec -it spark-worker-2 pip3 install vncorenlp




docker exec -it spark-worker-3 apk update
docker exec -it spark-worker-3 python3 -m pip install --upgrade pip
docker exec -it spark-worker-3 apk add --no-cache python3-dev py3-pip build-base
docker exec -it spark-worker-3 apk add --no-cache lapack-dev libexecinfo-dev
docker exec -it spark-worker-3 apk add build-base python3-dev
docker exec -it spark-worker-3 python3 -m ensurepip --default-pip
docker exec -it spark-worker-3 wget https://bootstrap.pypa.io/get-pip.py get-pip.py
docker exec -it spark-worker-3 python3 get-pip.py
docker exec -it spark-worker-3 pip install --upgrade pip setuptools
docker exec -it spark-worker-3 pip3 install numpy --compile --pre
docker exec -it spark-worker-3 pip3 install sparknlp
docker exec -it spark-worker-3 pip3 install kafka-python
docker exec -it spark-worker-3 pip3 install hdfs
docker exec spark-worker-3 apk add gfortran
docker exec -it spark-worker-3 pip3 install pandas
docker exec -it spark-worker-3 pip3 install cassandra-driver
docker exec -it spark-worker-3 pip3 install vncorenlp
