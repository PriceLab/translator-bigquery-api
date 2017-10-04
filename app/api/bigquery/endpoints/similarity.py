
import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import list_files 
from app.api.bigquery.serializers import test_serializer 
from app.api.restplus import api
from app.database.models import TestModel 

log = logging.getLogger(__name__)

ns = api.namespace('similarity', 
        description="""Access the similarity profiles of various
        entities
        """)

@ns.route('/similarity/<string:request_id>')
class Similarity(Resource):
    def get(self, request_id):
        pass
