#/bin/bash

docker stop translator-bigquery-app 

docker rm translator-bigquery-app 

./start_service.sh
