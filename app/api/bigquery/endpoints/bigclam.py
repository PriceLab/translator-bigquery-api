import logging

from flask import request
from flask_restplus import Resource
from app.api.bigquery.business_interactions import get_request_status, run_bigclam_g2g_query, run_bigclam_g2d_query, ndex
from app.api.bigquery.serializers import bigclam_query_request, query_status_response, query_response, ndex_request, ndex_response
from app.api.bigquery.parsers import bigclam_query_url_parser

from app.api.restplus import api
from app.database.models import TestModel 
from app import settings

log = logging.getLogger(__name__)

ns = api.namespace('bigclam', 
        description="""Associations between genomic aberrations, gene knockdowns and drug response in cell lines.""")

@ns.route('/g2d/query')
class BigclamQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bigclam_query_url_parser, validate=False)
    def get(self):
        """Genomic aberrations in INPUT genes lead to sensitivity to OUTPUT drugs."""
        log.info("Initiating query")
        results = run_bigclam_g2d_query(request.values.to_dict())
        log.info("Query submission finished")
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bigclam_query_request)
    def post(self):
        """ Genomic aberrations in INPUT genes lead to sensitivity to OUTPUT drugs"""
        results = run_bigclam_g2d_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

@ns.route('/g2g/query')
class BigclamQuery(Resource):
    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bigclam_query_url_parser, validate=False)
    def get(self):
        """Genomic aberrations in INPUT genes decrease viability upon knockdown of OUTPUT genes"""
        log.info("Initiating query")
        results = run_bigclam_g2g_query(request.values.to_dict())
        log.info("Query submission finished")
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

    @ns.response(400, "Bad query request.")
    @ns.response(200, "OK")
    @ns.doc(model=query_response)
    @ns.expect(bigclam_query_request)
    def post(self):
        """Genomic aberrations in INPUT genes decrease viability upon knockdown of OUTPUT genes"""
        results = run_bigclam_g2g_query(request.json)
        if results['status'] == 'error':
            log.debug("Error in query %s" % (results))
            return results, 400
        else:
            log.debug("Valid request %s" % (results))
            return results, 200

