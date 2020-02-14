import sys
sys.path.append('/')

from behave import *
from mock import *

def before_all(context):
    # initiate mock object
    if 'googleinterface' in context:
        googleinterface = context.googleinterface
    else:
        googleinterface = Mock()
    context.googleinterface = googleinterface

    # set valid BigGIM parameters
    valid_attributes = {'average_columns': False,
        'columns': ['TCGA_GBM_Correlation', 'TCGA_GBM_Pvalue', 'GTEx_Brain_Correlation', 'GTEx_Brain_Pvalue'],
        'ids1': ['5111', '6996', '57697', '6815', '889', '7112', '2176', '1019', '5888', '5706'],
        'ids2': ['5111', '6996', '57697', '6815', '889', '7112', '2176', '1019', '5888', '5706'],
        'limit': 40000,
        'restriction_bool': [('BioGRID_Interaction', 'True')],
        'restriction_gt': [('TCGA_GBM_Correlation', '.2'), ('GTEx_Brain_Correlation', '.2')],
        'restriction_join': 'intersect',
        'restriction_lt': [('TCGA_GBM_Pvalue', '1.3'), ('GTEx_Brain_Pvalue', '1.3')],
        'table': 'BigGIM_70_v1'}
    context.valid_biggim_attribute = valid_attributes

    # mock BigQuery attributes
    mock_schema = [Mock() for col in valid_attributes['columns']]
    counter = 0
    for mock_obj in mock_schema:
        mock_obj.name = valid_attributes['columns'][counter]
        counter += 1
    context.mock_table_schema = mock_schema

    # mock BigQuery query
    mock_bq_client = Mock()
    mock_bq_client.run_async_query.return_value = {
    "status": "submitted",
    "request_id": "77dae546-b1e4-433e-9b47-4de68fe35686"
    }
    context.bq_client = mock_bq_client
