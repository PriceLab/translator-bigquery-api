from flask_restplus import fields
from app.api.restplus import api
from app import settings

# specifications for json request objects

test_serializer = api.model('Test Model', {
        'id': fields.Integer(readOnly=True, description='The id for a test model'),
        'name': fields.Integer(readOnly=True, description='The name for a test model'),
    })


query_request = api.model('Query request',{
    'ids1': fields.String( required=False,
                        example="55120,2189,57697",
                        description="""A comma delimited list of Entrez gene ids to select.
                    
**Default**: all genes.
"""
                        ),
    'ids2': fields.String(description="""Entrez gene ids to select.

If not given, the query selects any gene related to a gene in ids 1.
If given, the query only selects relations that contain a gene in ids1 and a gene in ids2.

**Default**: all genes.
""",                      required=False,
                          example='55120,2189,57697,79728,171017'),

    'columns':fields.String(description="""A comma delimited list of column names to return.

Gene ids are always returned and do not need to be specified. If a column is not present, then an error is returned.

Available columns are provided by `/api/metadata/tables/{table_name}/columns`.

**Default**: all columns.
""",
                          required=False,
                          example = 'TCGA_GBM_Pvalue,TCGA_GBM_Correlation, GTEx_Brain_Correlation,GTEx_Brain_Pvalue'),
    'restriction_lt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is less than the given value.
""",
    example='TCGA_GBM_Pvalue,.05, GTEx_Brain_Pvalue,.05'
    ),
    'restriction_gt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is greater than the given value.
""",
    example='TCGA_GBM_Correlation,.7, GTEx_Brain_Correlation,.8'
    ),

    'table':fields.String(description="""
The table to select from.

Available tables are provided by  `/api/metadata/tables`.

**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE,
    example=settings.BIGQUERY_DEFAULT_TABLE
    )

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
