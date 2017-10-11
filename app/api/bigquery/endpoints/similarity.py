
import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files, get_request_status, run_query
from app.api.bigquery.serializers import test_serializer, request_get, query_request
#from app.api.bigquery.parsers import query_arguments

from app.api.restplus import api
from app.database.models import TestModel 

log = logging.getLogger(__name__)

ns = api.namespace('similarity', 
        description="""Access the similarity profiles of various
        entities
        """)





@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/query/status/<string:request_id>')
class SimilarityStatus(Resource):
    @ns.response(404, "Request Id not found.")
    @ns.response(200, "OK")
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
    @ns.expect(query_request)
    def post(self):
        """Submit a new query request."""
        results = run_query(request)
        if 'error' in results:
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200
