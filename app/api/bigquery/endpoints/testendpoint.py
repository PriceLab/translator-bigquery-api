import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business import test_business
from app.api.bigquery.serializers import test_serializer 
from app.api.restplus import api
from app.database.models import TestModel 

log = logging.getLogger(__name__)

ns = api.namespace('testendpoint', 
        description='This is a test endpoint')

@ns.route('/te/<int:id>')
class TestEndpoint(Resource):
    def get(self, id):
        return id

