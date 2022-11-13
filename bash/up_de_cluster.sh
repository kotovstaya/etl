#! /bin/bash

echo -e "AIRFLOW_UID=$(id -u)" > .env
docker-compose -f ./../de_cluster.yaml up
