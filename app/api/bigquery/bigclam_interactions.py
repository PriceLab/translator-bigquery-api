from app.api.bigquery.bigclam import *
from app.api.bigquery.querytools import GoogleInterface

glogger = logging.getLogger()

def run_bigclam_g2g_query(request):
    """
    Takes a request object and runs a gene to gene query.

    If successful it returns the request id, if unsuccessful it
    returns an error.
    """
    qb = BCQueryBuilder.from_request(request, 'g2g' )
    errors = qb.validate_query()
    if len(errors):
        return {'status':'error',
                'message': '\n'.join(errors)}
    else:
        query = qb.generate_query()
        gi = GoogleInterface()
        request_id = gi.query(query)
        return {'status':'submitted', 'request_id':request_id}

def run_bigclam_g2d_query(request):
    """
    Takes a request object and runs a gene to drugs query.

    If successful it returns the request id, if unsuccessful it
    returns an error.
    """
    qb = BCQueryBuilder.from_request(request, 'g2d' )
    errors = qb.validate_query()
    if len(errors):
        return {'status':'error',
                'message': '\n'.join(errors)}
    else:
        query = qb.generate_query()
        gi = GoogleInterface()
        request_id = gi.query(query)
        return {'status':'submitted', 'request_id':request_id}
