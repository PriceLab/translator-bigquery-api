
import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files, get_request_status, run_query
from app.api.bigquery.serializers import test_serializer, request_get
from app.api.restplus import api
from app.database.models import TestModel 

log = logging.getLogger(__name__)

ns = api.namespace('similarity', 
        description="""Access the similarity profiles of various
        entities
        """)

@ns.route('/query')
class Similarity(Resource):
    def get(self):
        """Posts a test query"""
        test_query = """SELECT * FROM [isb-cgc-04-0010:NTTB_MERGE.FA_90_v0] LIMIT 10"""
        request_id = run_query(test_query)
        return {'request_id':request_id}




@ns.doc(params={'request_id': 'The request id for a query'})
@ns.route('/status/<string:request_id>')
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
