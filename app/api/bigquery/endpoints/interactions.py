
import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import get_request_status, run_query, ndex
from app.api.bigquery.serializers import query_request, query_status_response, query_response, ndex_request, ndex_response
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.models import TestModel 
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('interactions', 
        description="""Mine the interaction profiles of various
        entities
        """)

@ns.route('/ndex')
class NDExSubmit(Resource):
    @ns.doc(model=ndex_response)
    @ns.expect(ndex_request)
    def post(self):
        log.info("%s" % (str(request.json),))
        response = ndex(request.json)
        code = 200 if response['status'] == 'complete' else 404
        return response, code

@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/ndex/<string:request_id>')
class NDExSubmit(Resource):
    @ns.doc(model=ndex_response)
    def get(self, request_id):
        log.info("%s" % (str(request.json),))
        r = {'request_id': request_id}
        response = ndex(r)
        code = 200 if response['status'] == 'complete' else 404
        return response, code

@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/query/status/<string:request_id>')
class InteractionsStatus(Resource):
    @ns.doc( model=query_status_response, 
            responses={'200':'OK', '404': 'Request id not found'})
    def get(self, request_id):
        """Gets the status of a query request"""
        result = get_request_status(request_id)
        if result['status'] == 'error':
            return result, 404
        else:
            return result, 200

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
