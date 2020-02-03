import sys, mock
sys.path.append('/')

from uuid import *
from behave import *
from app.api.bigquery.querytools import *
from app.api.bigquery.business_interactions import *
from mock import *

def validate_uuid(id):
    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        assert(False)

    return (str(uuid_obj) == id)

@then('the query gets a request id')
def step_get_request_id(context):
    with mock.patch('google.cloud.bigquery.Client') as mock_google:
        mock_google.from_service_account_json = Mock()
        mock_google.from_service_account_json().run_async_query = Mock()

        gi = GoogleInterface()
        request_id = gi.query(context.request)

        assert mock_google.from_service_account_json().run_async_query.call_count > 0
        assert validate_uuid(request_id)

@then('the resulting status message says submitted')
def step_get_no_error_message(context):
    with mock.patch('app.api.bigquery.querytools.GoogleInterface') as mock_googleinterface:
        with mock.patch('google.cloud.bigquery.Client') as mock_google:
            mock_googleinterface().bq_client = MagicMock()
            mock_googleinterface().bq_client.dataset = Mock()
            mock_googleinterface().bq_client.dataset().table = Mock()
            mock_googleinterface().bq_client.dataset().table().schema = context.mock_table_schema
            mock_google.from_service_account_json = Mock()
            mock_google.from_service_account_json().run_async_query = Mock()

            results = run_query(context.request)

            assert mock_google.from_service_account_json().run_async_query.call_count > 0
            assert results['status'] == 'submitted'
            assert validate_uuid(results['request_id'])

@then('the resulting status message says errors with error messages')
def step_get_error_messages(context):
    with mock.patch('app.api.bigquery.querytools.GoogleInterface') as mock_googleinterface:
        with mock.patch('google.cloud.bigquery.Client') as mock_google:
            mock_googleinterface().bq_client = MagicMock()
            mock_googleinterface().bq_client.dataset = Mock()
            mock_googleinterface().bq_client.dataset().table = Mock()
            mock_googleinterface().bq_client.dataset().table().schema = context.mock_table_schema
            mock_google.from_service_account_json = Mock()
            mock_google.from_service_account_json().run_async_query = Mock()

            match_table = context.processed_request._table == context.valid_biggim_attribute['table']
            mock_googleinterface().bq_client.dataset().table().exists = Mock(return_value=match_table)
            results = run_query(context.request)

            assert mock_google.from_service_account_json().run_async_query.call_count == 0
            assert results['status'] == 'error'
            assert len(results['message']) > 0
