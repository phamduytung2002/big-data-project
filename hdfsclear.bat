docker exec -it namenode hdfs dfsadmin -safemode leave
docker exec -it namenode hadoop dfs -rm -r /user
docker exec -it namenode hdfs dfs -mkdir /user
docker exec -it namenode hdfs dfs -mkdir /user/pdt
docker exec -it namenode hdfs dfs -mkdir /user/pdt/news
docker exec -it namenode hdfs dfs -mkdir /user/pdt/processed

docker exec -it namenode hdfs dfs -ls /