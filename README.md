# translator-bigquery-api

This is the API for the Translator BigGIM BigQuery Project

Runs the BigGIM Flask API using uwsgi and nginx controlled by supervisor

The BigGIM API allows researchers to query 

***

## Running

To run this API locally, you must first build with:
> docker-compose build

To start the container after it is built, run:
> docker-compose up

To stop the container, run:
> docker-compose stop

To stop and destroy the container, run:
> docker-compose down

To see which port the container is running on:
> docker-compose ps

***

## Building

This repository uses a 4 stage build process:


1) python:2.7

	The python image is built on debian

2) uwsgi-nginx-docker
	
	The uwsgi-nginx-docker image installs the following with apt-get:
	- uwsgi = an application server used here to run python
	- nginx = a web server used to send requests to python via uwsgi or serve content
	- supervisord = a process monitoring software that starts and monitors uwsgi and nginx

	It contains two configs:
	- supervisord.conf = configuration for supervisord to start uwsgi in /usr/local/bin
	    and nginx in /usr/sbin
	- uwsgi.ini = configuration file for uwsgi

	It creates two scripts:
	- start.sh = starts /usr/bin/supervisord
	- entrypoint.sh =  creates a general nginx configuration in /etc/nginx/nginx.conf,
	   an application specific configuration in  /etc/nginx/conf.d/nginx.conf,
	   then runs the command passed in
	  eg: docker run my_image server start = server start

	It copies ./app to /app and sets WORKDIR /app 
	ENTRYPOINT is set as ./entrypoint.sh
	CMD is set as ./start.sh

	ENTRYPOINT is always run
	CMD is run when the container is started with no command

	Thus this container will always run entrypoint.sh to create the nginx.conf and then
	run the start.sh to start supervisord to start nginx and uwsgi

	The demo application is a uwsgi Python app

3) uwsgi-nginx-flask-docker

	The uwsgi-nginx-flask-docker image uses the previous image and then installs flask

	It replaces the previous image entrypoint.sh to create a nginx application specific
	configuration in /etc/nginx/conf.d/nginx.conf that has a static url location

	The demo application is a uwsgi Flask app

4) translator-bigquery-api

   Replaces the demo application with the BigGIM Flask API that queries BigQuery

   As previous image does, uses entrypoint.sh to create a nginx configuration file and
   start.sh to start supervisord to run uwsgi and nginx

