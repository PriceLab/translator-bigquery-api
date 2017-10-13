import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files, get_request_status, run_query
from app.api.bigquery.serializers import query_request, query_status_response, query_response
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.helpers import populate_database
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('metadata', 
        description="""Access the metadata for available datasets. 
        """)

@ns.doc(params={'table_name': 'the name of a biqquery table'})
@ns.route('/table/<string:table_name>')
class MetadataTableResource(Resource):

    def get(self, table_name):
        """Retrieve metadata about a table"""
        if table_name is None:
            return ['All tables'], 200
        else:
            return [table_name], 200

@ns.route('/table')
class MetadataTableResources(Resource):
    def get(self):
        """Retrieve list of available tables"""
        return ['All tables'], 200


@ns.route('/init_db')
class Initdb(Resource):
    def get(self):
        populate_database()
