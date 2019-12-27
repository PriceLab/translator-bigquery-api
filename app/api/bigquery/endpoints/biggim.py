import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import run_query
from app.api.bigquery.serializers import query_request, query_response
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.models import TestModel
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('biggim',
        description="""Comprehensive querying of gene to gene interactions under different tissue types.""")

@ns.route('/query')
class InteractionsQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(query_url_parser, validate=False)
    def get(self):
        """Submit a new query request."""
        log.info("Initiating query")
        results = run_query(request.values.to_dict())
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
    @ns.expect(query_request)
    def post(self):
        """Submit a new query request."""
        results = run_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200
