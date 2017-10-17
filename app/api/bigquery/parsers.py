from flask_restplus import reqparse
from app import settings

# common args

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('bool', type=bool, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')



query_url_parser = reqparse.RequestParser() 
query_url_parser.add_argument('ids1', help="""A comma delimited list of Entrez gene ids to select.
                
**Default**: all genes.

**Example**:"5111,6996,57697,6815,889,7112,2176,1019,5888,5706"
""")
query_url_parser.add_argument( 'ids2', help="""Entrez gene ids to select.

If not given, the query selects any gene related to a gene in ids 1.
If given, the query only selects relations that contain a gene in ids1 and a gene in ids2.

**Default**: all genes.

**Example**:"5111,6996,57697,6815,889,7112,2176,1019,5888,5706"
""")
query_url_parser.add_argument( 'columns', help="""A comma delimited list of column names to return.

Gene ids are always returned and do not need to be specified. If a column is not present, then an error is returned.

Available columns are provided by `/api/metadata/tables/{table_name}/columns`.

**Default**: all columns.

**Example**: TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation,GTEx_Brain_Pvalue
""")
query_url_parser.add_argument('restriction_lt', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is less than the given value.

**Default**: No restrictions

**Example**:TCGA_GBM_Pvalue,.05, GTEx_Brain_Pvalue,.05
""")
query_url_parser.add_argument( 'restriction_gt', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is greater than the given value.

**Default**: No restrictions

**Example**: TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2
""")
query_url_parser.add_argument( 'restriction_bool', help="""
A list of pairs of values `column name,value` with which to restrict the results of the query to rows where the value of the column is True or False.

**Default**: No restrictions

**Example**: BioGRID_Interaction,True
""")
query_url_parser.add_argument( 'restriction_join', help="""
The type of join made on restrictions. Either `intersect` or `union`

**Default**: intersect

**Example**: intersect
""")
query_url_parser.add_argument('table', help="""
The table to select from.

Available tables are provided by  `/api/metadata/tables`.

**Default**: %s
""" % settings.BIGQUERY_DEFAULT_TABLE
)

query_url_parser.add_argument('limit', help="""
The maximum number of rows to return.


**Default**: 10000
""" )
