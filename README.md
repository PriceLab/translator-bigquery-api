# translator-bigquery-api

This is the API for the Translator BigGIM BigQuery Project

Runs the BigGIM Flask API using uwsgi and nginx controlled by supervisor

***

## BigGIM

Big GIM stands for Gene Interaction Miner.  Big GIM is a set of Google BigQuery
tables that contain interaction data for pairs of genes in 4 areas:
1) tissue-specific gene expression correlations from healthy tissue (GTEx)
2) tissue-specific gene expression correlations from cancer samples (TCGA)
3) tissue-specific probabilities of function interaction (GIANT)
4) direct gene interactions (BioGRID)

1 and 2 were computed using Spearman rank correlation using MATLAB for all
pairs of genes in the data where the coefficient of variation of the expression
of both genes was at least 0.05, the number of samples with gene expression values
greater than 0 is at least 5, there are at least 25 samples with expression values
for both genes.

BigGIM_70 = R value of .7 to be kept
BigGIM_80 = R value of .8 to be kept
BigGIM_90 = R value of .9 to be kept

## LittleGIM

LittleGIM uses a specific set of defaults to query BigGIM resources and returns
an average of the results across the samples.

Defaults:
 - Looks at the 'whole_body' tissue samples only
 - minR of 0.3
 - limit 10,000
 - Spearman Rank Correlation Coefficient

## BigCLAM

BigCLAM stands for Big Cell Line Association Miner.  BigCLAM is a set of Google BigQuery
tables that contain cell line data for copy number variations, gene symbol associations,
WES gene variants, and drug associations.


## Architecture

The project is built in three layers:

The exterior layer is the endpoints in /app/api/bigquery/endpoints.  They are kept as simple as possible so that they handle the request and return valid results or an error.  Flask Restplus uses serializers.py and parsers.py to validate the input, encode the output, and generate the Swagger documentation for the endpoints, which are connected via namespace decorators.

The interior layer is the models in bglite.py, bigclam.py, and querytools.py (aka biggim.py).  These classes handle querying their specific resource and include SQL.  The querytools.py contains much of the mechanics of making bigquery requests and could be extracted into a separate class that is used by a new biggim.py and by bglite.py but bigclam.py does not use the bigquery request mechanics in querytools.

The connecting layer (aka the business logic layer) is encoded in business_interactions.py where the classes in the interior layer are instantiated and the request parameters from the exterior layer are connected and validated and the appropriate query for the request is executed.

## Running

To run this API locally, you must first build with:
> docker-compose build

To start the container after it is built, run:
> docker-compose up

The default URL for the API when started via docker-compose is:
http://localhost/api/

This URL can be configured in the docker-compose.yml by editing
the FLASK_SERVER_NAME variable

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

## Use Cases

This API supports querying the following resources:
- Gene Interaction Networks
- Cell Line Associations
- Gene to Drug associations
- Gene to Gene associations
- Gene and Tissue to Gene associations



## Citations

GIANT
Greene CS*, Krishnan A*, Wong AK*, Ricciotti E, Zelaya RA, Himmelstein DS, Zhang R, Hartmann BM, Zaslavsky E, Sealfon SC, Chasman DI, FitzGerald GA, Dolinski K, Grosser T, Troyanskaya OG. (2015). Understanding multicellular function and disease with human tissue-specific networks. Nature Genetics. 10.1038/ng.3259w.

BioGRID
Stark C, Breitkreutz BJ, Reguly T, Boucher L, Breitkreutz A, Tyers M. Biogrid: A General Repository for Interaction Datasets. Nucleic Acids Res. Jan 1, 2006; 34:D535-9.

GTEx
The Genotype-Tissue Expression (GTEx) Project was supported by the Common Fund of the Office of the Director of the National Institutes of Health, and by NCI, NHGRI, NHLBI, NIDA, NIMH, and NINDS. The data used for the analyses are V6 downloaded from the GTEx Portal.

TCGA
TCGA gene expression was downloaded from https://gdc.cancer.gov/node/905/ file:
http://api.gdc.cancer.gov/data/3586c0da-64d0-4b74-a449-5ff4d9136611
EBPlusPlusAdjustPANCAN_IlluminaHiSeq_RNASeqV2.geneExp.tsv
