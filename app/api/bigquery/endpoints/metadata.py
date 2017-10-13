import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files, get_request_status, run_query
from app.api.bigquery.serializers import table_response, column_response
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.helpers import populate_database
from app.database.models import *
from app import settings
from app.database import db

log = logging.getLogger(__name__)

ns = api.namespace('metadata', 
        description="""Access the metadata for available datasets. 
        """)

@ns.doc(params={'table_name': 'the name of a biqquery table'})
@ns.route('/table/<string:table_name>')
class MetadataTableResource(Resource):

    @ns.marshal_with(table_response)
    def get(self, table_name):
        """Retrieve metadata about a table"""
        table = Table.query.filter_by(name=table_name).first()
        if table is None:
            return {'status': 'error', 'message': 'Table not found'}, 404
        else:
            return table

@ns.doc(params={'table_name': 'the name of a biqquery table'})
@ns.doc(params={'column_name': 'the name of a column in this biqquery table'})

@ns.route('/table/<string:table_name>/<string:column_name>')
class MetadataColumnResource(Resource):

    @ns.marshal_with(column_response)
    def get(self, table_name, column_name):
        """Retrieve metadata about a table"""
        table = Table.query.filter_by(name=table_name).first()
        column = Column.query.filter_by(name=column_name, 
                                        table_id=table.id)
        cdict = dict(column)
        substudy = Substudy.query.get(id=column.substudy_id)   
        ssdict = dict(substudy)

        study = Study.query.get(substudy.study_id)
        ssdict['study'] = dict(study)
        cdict['substudy'] = ssdict
        return cdict


@ns.route('/table')
class MetadataTableResources(Resource):
    @ns.marshal_with(table_response)
    def get(self):
        """Retrieve list of available tables"""
        ds = Dataset.query.filter_by(name=settings.BIGQUERY_DATASET).first()
        return Table.query.filter_by(dataset_id=ds.id).all()

@ns.route('/init_db')
class Initdb(Resource):
    def get(self):
        populate_database()
