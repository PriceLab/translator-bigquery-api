
import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files, get_request_status, run_query
from app.api.bigquery.serializers import query_request, query_status_response, query_response
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.models import TestModel 
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('similarity', 
        description="""Access the similarity profiles of various
        entities
        """)


@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/query/status/<string:request_id>')
class SimilarityStatus(Resource):
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
class SimilarityQuery(Resource):
    
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(query_url_parser, validate=False)
    def get(self):
        """Submit a new query request."""
        results = run_query(request.values.to_dict())
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
