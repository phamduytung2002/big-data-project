#!/bin/bash

# Set Cassandra host and port
CASSANDRA_HOST="localhost"
CASSANDRA_PORT="9042"

# Set the path to your CQL file
CQL_FILE="database.cql"

# Run CQL script using cqlsh
cqlsh $CASSANDRA_HOST $CASSANDRA_PORT -f $CQL_FILE

# Check if the script executed successfully
if [ $? -eq 0 ]; then
    echo "CQL script executed successfully."
else
    echo "Error executing CQL script."
fi
