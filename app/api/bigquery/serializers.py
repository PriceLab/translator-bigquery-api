from flask_restplus import fields
from app.api.restplus import api
from app import settings

# specifications for json request objects

query_request = api.model('Query request',{
    'ids1': fields.String(description="A comma delimited list of Entrez gene ids to select.\n**Default**: all genes.",
        required=False,
        example="5111,6996,57697,6815,889,7112,2176,1019,5888,5706",
    ),
    'ids2': fields.String(description="""Entrez gene ids to select.\n
If not given, the query selects any gene related to a gene in ids 1.\n
If given, the query only selects relations that contain a gene in ids1 and a gene in ids2.\n
**Default**: all genes.
""",
        required=False,
        example='5111,6996,57697,6815,889,7112,2176,1019,5888,5706'
    ),
    'columns':fields.String(description="""A comma delimited list of column names to return.\n
Gene ids are always returned and do not need to be specified. If a column is not present, then an error is returned.\n
Available columns are provided by `/api/metadata/tables/{table_name}/columns`.\n
**Default**: all columns.
""",
        required=False,
        example = 'TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation,GTEx_Brain_Pvalue'
    ),
    'restriction_lt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is less than the given value.
""",
        example='TCGA_GBM_Pvalue,1.3, GTEx_Brain_Pvalue,1.3'
    ),
    'restriction_gt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is greater than the given value.
""",
        required=False,
        example='TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2'
    ),
    'restriction_bool': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is True or False.
""",
        required=False,
        example='BioGRID_Interaction,True'
    ),
    'restriction_join': fields.String(description="The type of join made on restrictions.\n**Default**: intersect",
        required=False,
        example='intersect',
        enum=['intersect','union']
    ),
    'average_columns': fields.Boolean(description="Return average over all columns as `mean`.",
            required=False,
            example=False,
            default=False
    ),
    'limit': fields.Integer(description="The maximum number of rows to return.\n**Default**: 10000",
        required=False,
        example=10000
    ),
    'table':fields.String(description="""The table to select from.\n
Available tables are provided by  `/api/metadata/tables`.\n
**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE,
        example=settings.BIGQUERY_DEFAULT_TABLE
    )
})


ndex_request = api.model('NDEx submit', {
    'request_id': fields.String(description="""The request id for a biggim query""",
        example='7f93cd6c-cc68-4c86-bfaa-8e2cc24ac94f'),
    'username':fields.String(description="A valid NDEx username. By default uses [biggim]",
        example="biggim", required=False),
    'password':fields.String(description="A valid NDEx password. By default uses [ncats]",
        example="ncats", required=False),
    'network_name':fields.String(description="A name for the network",
        example="My Network", required=False),
    'network_set':fields.String(description="An ndex network set in which to put your generated networks.",
        example="Anonymous", required=False)
})

ndex_response = api.model('NDEx response', {
    'request_id': fields.String(description="""The request id for a biggim query""",
        example='7f93cd6c-cc68-4c86-bfaa-8e2cc24ac94f'),
     'ndex_network_url': fields.List(
                fields.String(
                    description="The NDEx network url",
                    example="",),
                description="A list of NDEx urls"),
     'ndex_public_url': fields.List(
                fields.String(
                    description="The NDEx public url",
                    example="",),
                description="A list of NDEx urls"),
     'ndex_network_uuid': fields.List(
                fields.String(
                    description="The NDEx network uuid",
                    example="http://public.ndexbio.org/v2/network/c8d4d10d-f56d-11e7-adc1-0ac135e8bacf",),
                description="A list of NDEx uuids")
        })

query_status = api.model('Query request id', {
        'request_id': fields.String(
            pattern='[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
            description='The request id for this query as UUID',
            required=True
            ),
})

query_status_response = api.model('Query request status', {
        'request_id': fields.String(
            pattern='[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
            readOnly=True,
            description='The request id for this query as UUID',
            required=True
            ),
        'status': fields.String(description="""The query status""", enum=['error', 'running', 'complete'], required=True),
        'rows': fields.Integer(description="""Number of rows returned"""),
        'request_uri':fields.List(fields.String, description="""List of uris of generated csvs"""),
        'size': fields.String(description="""Human readable total size of result"""),
        'processed_data':fields.String(description="""Human readable size of query scan(determines cost of bigquery)"""),
        'message': fields.String(description="""Error messages if status is __error__""")
        })

query_response = api.model('The query response', {
    'request_id' :  fields.String(readOnly=True,
            description='The request id generated.',
            ),
    'status': fields.String(readOnly=True,
            description='The status of the query job submission.',
            enum=['submitted', 'error'],
            required=True
            ),
        'message': fields.String(description="""Error messages if status is __error__""")
    })

table_response_short = api.model('Table', {
    'name' :fields.String(description="Table name"),
    'description' :fields.String(description="Table description"),
    'num_rows' :fields.Integer(description="Number of rows in table"),
    'num_bytes': fields.Integer(description="Number of bytes in table"),
    'default': fields.Boolean(description="Is default table")
    })

study_response = api.model('Study', {
        'name': fields.String(description='The name of this study'),
        'description': fields.String(description='The description of this study'),
    })

substudy_response = api.model('Substudy',{
    'name': fields.String(description="Sub-study name"),
    'description': fields.String(description="Substudy description"),
    'cell_of_origin': fields.String(description="The cell type used."),
    'tissue_hierarchy': fields.String(description="The Brenda tissue hierarchy of the cell of origin"),
    'study': fields.Nested(study_response)
    })

column_response = api.model('Column', {
    'name':fields.String(description="Column description"),
    'interactions_type':fields.String(description="The type of interaction measured"),
    'datatype': fields.String(description="The datatype"),
    'substudy': fields.Nested(substudy_response)
})

table_response = api.model('Table', {
    'name' :fields.String(description="Table name"),
    'description' :fields.String(description="Table description"),
    'num_rows' :fields.Integer(description="Number of rows in table"),
    'num_bytes': fields.Integer(description="Number of bytes in table"),
    'columns': fields.List(fields.Nested(column_response)),
    'default': fields.Boolean(description="Is default table")
    })

table_name_only = api.model('Table', {
    'name':fields.String(description="Table name")
    })

column_response_no_substudy = api.model('Column', {
    'name':fields.String(description="Column description"),
    'interactions_type':fields.String(description="The type of interaction measured"),
    'datatype': fields.String(description="The datatype"),
    'table': fields.Nested(table_name_only)
})

substudy_child = api.model('Substudy',{
    'name': fields.String(description="Sub-study name"),
    'description': fields.String(description="Substudy description"),
    'cell_of_origin': fields.String(description="The cell type used."),
    'tissue_hierarchy': fields.String(description="The Brenda tissue hierarchy of the cell of origin"),
    'columns': fields.List(fields.Nested(column_response_no_substudy))
    })


study_response_test = api.model('Study', {
        'name': fields.String(description='The name of this study'),
        'description': fields.String(description='The description of this study'),
        'substudies': fields.List( fields.Nested( substudy_child ))
    })

unique_tissue_list = api.model('Tissues', {'tissues': fields.List(
    fields.String( description="A tissue"))})

tissue_substudy = api.model('TissueSubstudies', {
    'tissue' : fields.String(description='The tissue'),
    'substudies': fields.List(fields.Nested(substudy_child))
    })

#BIGCLAM
bigclam_query_request = api.model('BigCLAMj request',{
    'ids': fields.String( required=True,
                        example="TCOF1,DDX46,COPE,RIPK1",
                        description="""A comma delimited list of HGNC gene ids to select..
"""
                        ),
    })

#LILGIM
bglite_query_request = api.model('lilGIM request',{
    'ids': fields.String( required=False,
                        example="5111,6996,57697,6815,889,7112,2176,1019,5888,5706",
                        description="A comma delimited list of entrez gene ids to select\n**Required**"
    ),
    'tissue': fields.String(required=False,
        example="urinary_bladder",
        description="The tissue to select from.\n**Default**: whole_body\n",
        default="whole_body"
    ),
    'limit': fields.Integer(description="The maximum number of rows to return.\n**Default**: 1000",
        required=False,
        example=10000,
        default=1000
        ),
    })

# TRANSLATOR COMMON
# Built using https://github.com/NCATS-Tangerine/translator-testing-framework/blob/master/features/microservices.feature
translator_edge = api.model('Translator Edge', {
    'id': fields.String(required=True,
        example="e00",
        description="Edge ID"
    ),
    'source_id': fields.String(required=True,
        example="ncbigene:354",
        description="Source of Edge",
    ),
    'target_id': fields.String(required=True,
        example="ncbigene:3486",
        description="Target of Edge"
    )
})


translator_options = api.model('Translator Query Options',{
    'columns':fields.String(description="""A comma delimited list of column names to return.\n
Gene ids are always returned and do not need to be specified. If a column is not present, then an error is returned.\n
Available columns are provided by `/api/metadata/tables/{table_name}/columns`.\n
**Default**: all columns.
""",
        required=False,
        example = 'TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation,GTEx_Brain_Pvalue'
    ),
    'restriction_lt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is less than the given value.
""",
        example='TCGA_GBM_Pvalue,1.3, GTEx_Brain_Pvalue,1.3'
    ),
    'restriction_gt': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is greater than the given value.
""",
        required=False,
        example='TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2'
    ),
    'restriction_bool': fields.String(description="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value
of the column is True or False.
""",
        required=False,
        example='BioGRID_Interaction,True'
    ),
    'restriction_join': fields.String(description="The type of join made on restrictions.\n**Default**: intersect",
        required=False,
        example='intersect',
        enum=['intersect','union']
    ),
    'average_columns': fields.Boolean(description="Return average over all columns as `mean`.",
            required=False,
            example=False,
            default=False
    ),
    'limit': fields.Integer(description="The maximum number of rows to return.\n**Default**: 10000",
        required=False,
        example=10000
    ),
    'table':fields.String(description="""The table to select from.\n
Available tables are provided by  `/api/metadata/tables`.\n
**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE,
        example=settings.BIGQUERY_DEFAULT_TABLE
    )
})

# TRANSLATOR QUERY GRAPH
translator_query_node = api.model('Translator Query Node', {
    'id': fields.String(required=True,
        example="n01",
        description="Node ID"
    ),
    'type': fields.String(required=True,
        example="gene",
        description="Node Type"
    ),
    'curie': fields.String(required=True,
        example="ncbigene:354",
        description="Node CURIE"
    )
})

translator_query_graph = api.model('Translator Query Graph', {
    'nodes': fields.List(fields.Nested(translator_query_node)),
    'edges': fields.List(fields.Nested(translator_edge)),
})

translator_query = api.model('NCATS Translator Query', {
    'message': fields.Nested(translator_query_graph),
    'query_options': fields.Nested(translator_options)
})

# TRANSLATOR KNOWLEDGE GRAPH
translator_knowledge_node = api.model('Translator Knowledge Node', {
    'id': fields.String(required=True,
        example="ncbigene:354",
        description="Node ID"
    ),
    'type': fields.String(required=True,
        example="gene",
        description="Node Type"
    ),
    'name': fields.String(required=True,
        example="KLK3",
        description="Node Name"
    )
})

translator_knowledge_graph = api.model('Translator Knowledge Graph', {
    'nodes': fields.List(fields.Nested(translator_knowledge_node)),
    'edges': fields.List(fields.Nested(translator_edge)),
})

translator_knowledge = api.model('NCATS Translator Knowledge Graph', {
    'message': fields.Nested(translator_knowledge_graph),
    'query_options': fields.Nested(translator_options)
})

# TRANSLATOR RESULT

translator_node_binding = api.model('Translator Node Binding', {
    'qg_id': fields.String(required=True,
        example="n01",
        description="Query Graph Node ID"
    ),
    'kg_id': fields.String(required=True,
        example="ncbigene:354",
        description="Knowledge Graph Node ID"
    )
})

translator_edge_binding = api.model('Translator Edge Binding', {
    'qg_id': fields.String(required=True,
        example="e01",
        description="Query Graph Edge ID"
    ),
    'kg_id': fields.String(required=True,
        example="ncbigene:354",
        description="Knowledge Graph Edge ID"
    )
})

translator_result = api.model('Translator Result', {
    'node_bindings': fields.List(fields.Nested(translator_node_binding)),
    'edge_bindings': fields.List(fields.Nested(translator_edge_binding))
})