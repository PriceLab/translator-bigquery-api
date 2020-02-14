#/bin/bash

now=$(date "+%Y.%m.%d-%H.%M.%S")

docker build -t translator-bigquery-api:$now .
if [ $? = 1 ] ; then
    echo "build failed."
    exit
fi
docker tag translator-bigquery-api:$now translator-bigquery-api:latest
