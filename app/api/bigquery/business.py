from app.database import db
from app.database.models import TestModel
from app import settings
from app.api.bigquery.querytools import *

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET

def test_business(data):
    return "test_business"


def list_files(request_id):
    pass


def get_request_status(request_id):
    gi = GoogleInterface()
    query_job_id = gi.get_query_job_id(request_id)
    glogger.debug("Searching for %s query job" % (query_job_id,))
    query_job = gi.get_job(query_job_id)

    result = {'request_id':request_id}
    if query_job is None:
        result['status'] = 'error'
        result['message'] = 'No such request'
    elif query_job.state != 'DONE':
        result['status'] = 'running'
        glogger.debug("%s query job still running" % (extract_job_id,))
        return result
    else:
        extract_job_id = gi.get_extract_job_id(request_id)
        glogger.debug("Searching for %s extract job" % (extract_job_id,))
        extract_job = gi.get_job(extract_job_id)
        if extract_job is None:
            result['status'] = 'error'
            result['message'] = 'No such request'
            glogger.debug("Extract job %s not found." % (extract_job_id,))
        elif extract_job.state != 'DONE':
            result['status'] = 'running'
        else:
            tbl = query_job.destination
            #glogger.debug("rows: %s" % (tbl.reload().num_rows,))
            result['request_uri'] = gi.get_urls( request_id ) 
            result['status'] = 'complete'
    return result

def run_query(request):
    """
    Takes a request object and runs a query.

    If successful it returns the request id, if unsuccessful it
    returns an error.
    """

    qb = QueryBuilder.from_request(request)
    errors = qb.validate_query()
    if len(errors):
        return {'status':'error',
                'message': '\n'.join(errors)}
    else:
        query = qb.generate_query()
        gi = GoogleInterface()
        request_id = gi.query(query)
        return {'status':'submitted', 'request_id':request_id}

