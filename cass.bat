docker cp database.cql cassandra-node:database.cql
docker exec cassandra-node cqlsh -f database.cql

docker exec kafka-1 /usr/bin/kafka-topics --create --zookeeper zookeeper:2181 --replication-factor 3 --partitions 3 --topic newsss