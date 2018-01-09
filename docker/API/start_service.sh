#/bin/bash

IMAGE=pricelab/translator-bigquery-api
APP_DIR=/home/ec2-user/translator-bigquery-api/app
CRED_DIR=/home/ec2-user/bq_cred

docker run -d --name translator-bigquery-app -p 80:80 -p 443:443 \
        -v $APP_DIR:/app \
        -v $CRED_DIR:/cred \
        $IMAGE
