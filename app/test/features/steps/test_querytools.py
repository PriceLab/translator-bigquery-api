import sys, mock
sys.path.append('/')

from behave import *
from app.api.bigquery.querytools import *
from mock import *

@given('an empty biggim request submitted')
def step_submit_empty_request(context):
    empty_request = {}
    context.request = QueryBuilder.from_request(empty_request)

@given('a biggim request with invalid "{argument_type}" of "{argument}"')
def step_submit_invalid_request(context, argument_type, argument):
    argument_type_parameters_map = {'genes': ['ids1', 'ids2'],
                        'columns': ['columns'],
                        'correlation threshold': ['restriction_gt'],
                        'pvalue threshold': ['restriction_lt'],
                        'join type': ['restriction_join'],
                        'limits': ['limit'],
                        'table': ['table'],
                        'restriction boolean': ['restriction_bool'],
                        'average columns': ['average_columns']
                        }
    request = {}

    parameters = list(argument_type_parameters_map[argument_type])
    for parameter in parameters:
        request[parameter] = argument

    print(request)
    context.request = QueryBuilder.from_request(request)

@given('a valid biggim request is provided')
def step_submit_valid_request(context):
    # generate request
    valid_request = {'average_columns': False,
                    'columns': 'TCGA_GBM_Correlation,TCGA_GBM_Pvalue,GTEx_Brain_Correlation,GTEx_Brain_Pvalue',
                    'ids1': '5111,6996,57697,6815,889,7112,2176,1019,5888,5706',
                    'ids2': '5111,6996,57697,6815,889,7112,2176,1019,5888,5706',
                    'limit': 40000,
                    'restriction_bool': 'BioGRID_Interaction,True',
                    'restriction_gt': 'TCGA_GBM_Correlation,.2, GTEx_Brain_Correlation,.2',
                    'restriction_join': 'intersect',
                    'restriction_lt': 'TCGA_GBM_Pvalue,1.3, GTEx_Brain_Pvalue,1.3',
                    'table': 'BigGIM_70_v1'}
    context.request = QueryBuilder.from_request(valid_request)


@then('no error messages are returned from biggim')
def step_get_no_error_message(context):
    with mock.patch('app.api.bigquery.querytools.GoogleInterface') as mock_googleinterface:
        with mock.patch('google.cloud.bigquery.Client') as mock_google:
            mock_googleinterface().bq_client = MagicMock()
            mock_googleinterface().bq_client.dataset = Mock()
            mock_googleinterface().bq_client.dataset().table = Mock()
            mock_googleinterface().bq_client.dataset().table().schema = context.mock_table_schema

            match_table = context.request._table == context.valid_biggim_attribute['table']
            mock_googleinterface().bq_client.dataset().table().exists = Mock(return_value=match_table)
            assert len(context.request.validate_query()) == 0

@then('a list of errors is returned from biggim')
def step_get_no_error_message(context):
    with mock.patch('app.api.bigquery.querytools.GoogleInterface') as mock_googleinterface:
        with mock.patch('google.cloud.bigquery.Client') as mock_google:
            mock_googleinterface().bq_client = MagicMock()
            mock_googleinterface().bq_client.dataset = Mock()
            mock_googleinterface().bq_client.dataset().table = Mock()
            mock_googleinterface().bq_client.dataset().table().schema = context.mock_table_schema

            match_table = context.request._table == context.valid_biggim_attribute['table']
            mock_googleinterface().bq_client.dataset().table().exists = Mock(return_value=match_table)
            assert len(context.request.validate_query()) != 0
