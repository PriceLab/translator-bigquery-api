# Parsing and running queries for Big GIM and BIG CLAM
This directory houses code for the parsing of requests, generation of queries, and interfacing with BigQuery

## 1. Requests are received at endpoints
Requests can either be made via command line or through the Swagger UI interface

## 2. Queries are parsed
- For requests to the Big GIM endpoint, requests are parsed to generate queries which are submitted to Google BigQuery using `querytools.py`
- For requests to the Big CLAM endpoint, results are parsed, a ndex request is made and sent, the results are handled and returned to users using `business_interactions.py`
- For requests to the Lil GIM endpoint, requests are processed through `bglite.py` with queries built and validated using `querytools.py`
- For requests to the interaction endpoint, requests are parsed and pushed to ndex using `business_interactions.py`
- For requests to the metadata endpoint, requests are handled and results are returned using `business_metadata.py`
