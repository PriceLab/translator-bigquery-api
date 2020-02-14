from flask_restplus import reqparse
from app import settings

# common args

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('bool', type=bool, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')



query_url_parser = reqparse.RequestParser()
query_url_parser.add_argument('ids1', help="""A comma delimited list of Entrez gene ids to select.\n
**Default**: all genes.\n
**Example**:"5111,6996,57697,6815,889,7112,2176,1019,5888,5706"
""")
query_url_parser.add_argument( 'ids2', help="""Entrez gene ids to select.
If not given, the query selects any gene related to a gene in ids 1.
If given, the query only selects relations that contain a gene in ids1 and a gene in ids2.\n
**Default**: all genes.\n
**Example**: "5111,6996,57697,6815,889,7112,2176,1019,5888,5706"
""")
query_url_parser.add_argument( 'columns', help="""A comma delimited list of column names to return.\n
Gene ids are always returned and do not need to be specified. If a column is not present, then an error is returned.\n
Available columns are provided by `/api/metadata/tables/{table_name}/columns`.\n
**Default**: all columns.\n
**Example**: TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation
""")
query_url_parser.add_argument('restriction_lt', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is less than the given value.\n
**Default**: No restrictions\n
**Example**:TCGA_GBM_Pvalue,1.3, GTEx_Brain_Pvalue,1.3
""")
query_url_parser.add_argument( 'restriction_gt', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is greater than the given value.\n
**Default**: No restrictions\n
**Example**: TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2
""")
query_url_parser.add_argument( 'restriction_bool', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is True or False.\n
**Default**: No restrictions\n
**Example**: BioGRID_Interaction,True
""")
query_url_parser.add_argument( 'restriction_join', help="""
The type of join made on restrictions. Either `intersect` or `union`\n
**Default**: intersect\n
**Example**: intersect
""")
query_url_parser.add_argument('table', help="""
The table to select from.\n
Available tables are provided by  `/api/metadata/tables`.\n
**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE
)

query_url_parser.add_argument('limit', help="""
The maximum number of rows to return.\n\n
**Default**: 10000
""" )
query_url_parser.add_argument('average_columns', help="""
The maximum number of rows to return.\n\n
**Default**: false
""" )


# bigclam
bigclam_query_url_parser = reqparse.RequestParser()
bigclam_query_url_parser.add_argument('ids', help="A comma delimited list of HGNC gene ids to select.", required=True)
bigclam_query_url_parser.add_argument('limit', help="""Maximum number of records to return.\n\n**Default**: 100""",
    required=False, default=100)


# biggim lite
bglite_query_url_parser = reqparse.RequestParser()
bglite_query_url_parser.add_argument('ids', help="""A comma delimited list of entrez gene ids to select.\n
**Required**\n\n
**Example**:"5111,6996,57697,6815,889,7112,2176,1019,5888,5706"
""", required=True)

bglite_query_url_parser.add_argument('tissue', help="""Tissue to query.\n
See `/metadata/tissue` for options.\n
**Default**: whole_body""", default='whole_body')

bglite_query_url_parser.add_argument('limit', help="""The maximum number of rows to return.\n
**Default**: 10000
""", default=1000 )

query_url_parser.add_argument('table', help="""The table to select from.\n
Available tables are provided by  `/api/metadata/tables`.\n
**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE,
default=settings.BIGQUERY_DEFAULT_TABLE
)
