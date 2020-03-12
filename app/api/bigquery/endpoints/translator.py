import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import run_query
from app.api.bigquery.serializers import query_response, translator
from app.api.bigquery.parsers import query_url_parser

from app.api.restplus import api
from app.database.models import TestModel
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('translator',
        description="""Query BigGIM following the NCATS Translator Reasoner Standard API.""")
@ns.route('/query')
class TranslatorQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(translator)
    def post(self):
        """Submit a new query request."""
        # only parse the query_graph from the message
        message = request.json.get('message')
        qg = message.get('query_graph')
        ids = [node['curie'].split(':')[1] for node in qg.get('nodes') if node['curie'].startswith('ncbigene:')]
        biggim_query = {
            "restriction_join": "intersect",
            "limit": 10000,
            "average_columns": False,
            "restriction_gt": "TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2",
            "restriction_lt": "TCGA_GBM_Pvalue,1.3, GTEx_Brain_Pvalue,1.3",
            "table": "BigGIM_70_v1",
            "restriction_bool": "BioGRID_Interaction,True",
            "columns": "TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation,GTEx_Brain_Pvalue",
            "ids1": ",".join(ids),
            "ids2":",".join(ids)
        }
        log.debug("BIGGIM QUERY FROM TRANSLATOR: {}".format(biggim_query))
        results = run_query(biggim_query)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200
