import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import get_request_status
from app.api.bigquery.serializers import query_status, query_status_response, ndex_request, ndex_response
from app.api.bigquery.ndex_interactions import ndex

from app.api.restplus import api
from app.api.bigquery.endpoints.bglite import ns as lilgim

from app.api.bigquery.endpoints.biggim import ns as biggim
from app.api.bigquery.endpoints.bigclam import ns as bigclam
from app.api.bigquery.endpoints.translator import ns as translator
log = logging.getLogger(__name__)

ns = api.namespace('results',
        description="""Retrieve (or send to NDEX) the results of queries """)

@ns.route('/ndex')
class NDExSubmit(Resource):
    @ns.doc(model=ndex_response)
    @ns.expect(ndex_request)
    def post(self):
        """Push a query result to NDEX"""
        log.info("%s" % (str(request.json),))
        response = ndex(request.json)
        code = 200 if response['status'] == 'complete' else 404
        return response, code

@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/ndex/<string:request_id>')
class NDExSubmit(Resource):
    @ns.doc(model=ndex_response)
    def get(self, request_id):
        """Push a query result to NDEX"""
        log.info("%s" % (str(request.json),))
        r = {'request_id': request_id}
        response = ndex(r)
        code = 200 if response['status'] == 'complete' else 404
        return response, code

@ns.doc(params={'request_id': 'The request id for this query as UUID'})
@ns.route('/status/<string:request_id>')
@lilgim.route('/status/<string:request_id>')
@biggim.route('/status/<string:request_id>')
@bigclam.route('/status/<string:request_id>')
@translator.route('/status/<string:request_id>')
class InteractionsStatus(Resource):
    @ns.doc(model=query_status_response,
            responses={'200':'OK', '404': 'Request id not found'})
    @lilgim.doc(model=query_status_response,
            responses={'200':'OK', '404': 'Request id not found'})
    @biggim.doc(model=query_status_response,
            responses={'200':'OK', '404': 'Request id not found'})
    @bigclam.doc(model=query_status_response,
            responses={'200':'OK', '404': 'Request id not found'})
    @translator.doc(model=query_status_response,
            responses={'200':'OK', '404': 'Request id not found'})
    def get(self, request_id):
        """Gets the status of a query request"""
        result = get_request_status(request_id)
        if result['status'] == 'error':
            return result, 404
        else:
            return result, 200
