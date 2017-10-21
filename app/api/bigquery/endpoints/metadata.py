import logging

from flask import request
from flask_restplus import Resource, marshal
from app.api.bigquery.serializers import table_response, column_response, substudy_response, study_response, study_response_test, table_response_short, unique_tissue_list, tissue_substudy
from app.api.bigquery.parsers import query_url_parser
from app.api.bigquery.business_metadata import *
from app.api.restplus import api
from app.database.helpers import populate_database
from app.database.models import *
from app import settings
from app.database import db
import json


log = logging.getLogger(__name__)

ns = api.namespace('metadata',
        description="""Access the metadata for available datasets.
        """)


@ns.route('/table')
class MetadataTableResources(Resource):
    @ns.marshal_with(table_response_short)
    def get(self):
        """Retrieve list of available tables"""
        tables = get_table()
        return tables, 200


@ns.response(404, "Table not found")
@ns.response(200, "OK")
@ns.doc(params={'table_name': 'the name of a biqquery table'})
@ns.route('/table/<string:table_name>')
class MetadataTableResource(Resource):
    @ns.marshal_with(table_response)
    def get(self, table_name):
        """Retrieve metadata about a table"""
        try:
            table = get_table(table_name)
            return table, 200
        except:
            ns.abort(404, status='error', message="[%s] not a valid table" % (str(table_name), ))


@ns.response(404, "Column not found")
@ns.response(200, "OK")
@ns.doc(params={'table_name': 'the name of a biqquery table'})
@ns.doc(params={'column_name': 'the name of a column in this biqquery table'})
@ns.route('/table/<string:table_name>/column/<string:column_name>')
class MetadataColumnResource(Resource):
    @ns.marshal_with(column_response)
    def get(self, table_name, column_name):
        """Retrieve metadata about a tables column."""
        try:
            column = get_column(table_name, column_name)
            return column, 200
        except:
            ns.abort(404, status='error', message="[%s.%s] not a valid column" % (str(table_name), str(column_name)))


@ns.route('/study')
class MetadataStudies(Resource):
    @ns.marshal_with(study_response_test)
    def get(self):
        """Return all available studies"""
        return Study.query.all()


@ns.response(404, "Study not found")
@ns.response(200, "OK")
@ns.doc(params={'study_name': 'the name of a Big GIM study'})
@ns.route('/study/<string:study_name>')
class MetadataStudy(Resource):
    """Return a single study and associated substudies"""
    @ns.marshal_with(study_response_test, code=200)
    def get(self, study_name):
        result =Study.query.filter_by(name=study_name).first()
        if result:
            return result, 200
        else:
            ns.abort(404, status='error', message="[%s] not a valid study" % (str(study_name),))


@ns.route('/tissue')
class Tissue(Resource):
    @ns.marshal_with(unique_tissue_list) 
    def get(self):
        """Return a list of available tissues"""
        tis = db.session.query(SubstudyTissue.tissue).distinct().all()
        return {'tissues':sorted([t[0] for t in tis])}, 200


@ns.response(200, "OK")
@ns.response(404, "Tissue not found")
@ns.doc(params={'tissue_name': 'the name of tissue'})
@ns.route('/tissue/<string:tissue_name>')
class Tissue(Resource):
    @ns.marshal_with(tissue_substudy)
    def get(self, tissue_name):
        """Return a list of substudies and columns associated with a tissue"""
        st = SubstudyTissue.query.filter_by(tissue=tissue_name).all()
        if st:
            substudies = []
            for s in st:
                substudies.append(Substudy.query.get(s.substudy_id))
            return {'tissue':tissue_name, 'substudies':substudies}, 200
        else:
            ns.abort(404, status='error', message="[%s] not a valid tissue" % (str(tissue_name),))


@ns.route('/init_db/<string:password>', doc=False)
class Initdb(Resource):
    def get(self, password):
        """This is a function that rebuilds the sqllite database"""
        import hashlib
        with open('/cred/database_reset.json') as pword_file:
            hashed = json.load(pword_file)
        if hashed['password'] == hashlib.sha224(password).hexdigest():
            populate_database()
        else:
            ns.abort(401, status='error', message="Not a valid password")
