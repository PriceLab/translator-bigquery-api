#/bin/bash

docker tag translator-bigquery-api:latest pricelab/translator-bigquery-api:latest
docker push pricelab/translator-bigquery-api:latest
