docker cp database.cql cassandra-node:database.cql
docker exec cassandra-node cqlsh -f database.cql