from app.database import db
from app.database.models import TestModel
from app import settings
from app.api.bigquery.querytools import *

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging
import math

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET


def get_request_status(request_id):

    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])
    gi = GoogleInterface()
    query_job_id = gi.get_query_job_id(request_id)
    glogger.debug("Searching for %s query job" % (query_job_id,))
    query_job = gi.get_job(query_job_id)
    ctr = 0
    while query_job is None:
        time.sleep(.5)
        query_job = gi.get_job(query_job_id)
        ctr += 1
        if ctr > 5:
            break
    result = {'request_id':request_id}
    if query_job is None:
        result['status'] = 'error'
        result['message'] = 'No such request - Missing query job.'
    elif query_job.state != 'DONE':
        result['status'] = 'running'
        result['message'] = 'Query job is running.'
        glogger.debug("%s query job still running" % (query_job_id,))
        return result
    elif query_job.errors == None:
        extract_job_id = gi.get_extract_job_id(request_id)
        glogger.debug("Searching for %s extract job" % (extract_job_id,))
        extract_job = gi.get_job(extract_job_id)
        ctr = 0
        while extract_job is None:
            time.sleep(1)
            extract_job = gi.get_job(extract_job_id)
            ctr += 1
            glogger.debug("Extract job not found.  May be between ej/qj")
            if ctr > 5:
                break
        if extract_job is None:
            result['status'] = 'error'
            result['message'] = 'Extraction not found. Might retry.'
            glogger.debug("Extract job %s not found." % (extract_job_id,))
        elif extract_job.state != 'DONE':
            result['status'] = 'running'
            result['message'] = 'Extraction job is running.'
        else:
            qr = query_job.query_results()
            result['rows'] = qr.total_rows
            result['processed_data'] = convert_size(qr.total_bytes_processed)
            total_file_size = 0
            for b in gi.list_blobs(prefix=request_id):
                total_file_size += b.size
            result['size'] = convert_size(total_file_size)
            #glogger.debug("rows: %s" % (tbl.reload().num_rows,))
            result['request_uri'] = gi.get_urls( request_id ) 
            result['status'] = 'complete'
    elif query_job.errors is not None:
        glogger.exception("Error in query job[%s]" % (str(query_job.errors),))
        result['status'] = 'error'
        result['message'] = ''
        for error in query_job.errors:
            result['message'] += "Query job failed with [%s]." % (error['reason'],)
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

