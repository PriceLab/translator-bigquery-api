import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import run_query
from app.api.bigquery.serializers import query_response, translator_query, translator_knowledge, translator_result
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.models import TestModel
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('translator',
        description="""Query BigGIM following the NCATS Translator Reasoner Standard API.""")
@ns.route('/query_graph')
class TranslatorQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(translator_query)
    def post(self):
        """Submit a new query request."""
        results = run_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

@ns.route('/query_knowledgegraph')
class TranslatorKnowledgeQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(translator_query)
    def post(self):
        """Submit a new query request."""
        results = run_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

@ns.route('/results')
class TranslatorKnowledgeQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(translator_result)
    def post(self):
        """Submit a new query request."""
        results = run_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200
