from flask_restplus import fields
from app.api.restplus import api

# specifications for json request objects

test_serializer = api.model('Test Model', {
        'id': fields.Integer(readOnly=True, description='The id for a test model'),
        'name': fields.Integer(readOnly=True, description='The name for a test model'),
    })




query_response = api.model('Query request response', {
        'request_id': fields.String(required=True,
            pattern='[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
            readOnly=True, 
            description='The request id for this query as UUID'),
    })

request_get = api.model('The status of a query request', {
    'request_id' :  fields.String(readOnly=True, 
            description='The request id for this query as UUID',
            pattern='[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
            required=True
            ),
    })

request_status = api.model('The status of a query request', {
    'request_id' :  fields.String(readOnly=True, 
            description='The request id for this query as UUID',
            pattern='[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
            required=True
            ),
    'status': fields.String(readOnly=True,
            description='The status of the query job',
            enum=['running', 'error', 'complete'],
            required=True
            ),
    'result_uri': fields.List(
            fields.String(readOnly=True,
            description="The public url of the query results as csv, this will be deleted 48 hrs. after it is generated.",
            ),
            required=False
            ),

    })
