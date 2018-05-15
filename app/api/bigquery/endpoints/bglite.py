import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import run_bglite_gt2g_query
from app.api.bigquery.serializers import bglite_query_request, query_status_response, query_response, ndex_request, ndex_response
from app.api.bigquery.parsers import bglite_query_url_parser

from app.api.restplus import api
from app.database.models import TestModel 
from app import settings

ns = api.namespace('lilgim', 
        description="""Simplified interface to BigGIM""")
log = logging.getLogger(__name__)

@ns.route('/query/gt2g')
class BGLiteQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bglite_query_url_parser, validate=False)
    def get(self):
        """Find tissue-specific correlated genes"""
        log.info("Initiating query")
        results = run_bglite_gt2g_query(request.values.to_dict())
        log.info("Query submission finished")
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bglite_query_request)
    def post(self):
        """Find tissue-specific correlated genes"""
        results = run_bglite_gt2g_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

