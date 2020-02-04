import sys
sys.path.append('/')

from behave import given, when, then
from mock import patch
from google.cloud.bigquery.query import QueryResults
from mock import *


from app.api.bigquery.business_interactions import get_request_status

@given('a successful request id')
def successful_request(context):
  context.request_id = "77dae546-b1e4-433e-9b47-4de68fe35686"

@given('an invalid request status query for "{request_id}"')
def invalid_request(context, request_id):
  context.request_id = request_id

@then('the API returns a complete request status')
def complete_request_status(context):
  print("context {}".format(context.__dict__))
  expected = {
    "status": "complete",
    "rows": 100,
    "processed_data": "1.03 GB",
    "request_id": "77dae546-b1e4-433e-9b47-4de68fe35686",
    "request_uri": [
      "https://storage.googleapis.com/ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv"
    ],
    "size": "4.16 KB"
  }

  googleinterface = context.googleinterface
  print(googleinterface.get_query_job_results.return_value)
  with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
    mock_googleinterface().get_query_job_results.return_value = googleinterface.get_query_job_results.return_value
    mock_googleinterface().get_extract_job.return_value = googleinterface.get_extract_job.return_value
    mock_googleinterface().get_urls.return_value = googleinterface.get_urls.return_value
    mock_googleinterface().list_blobs.return_value = googleinterface.list_blobs.return_value

    result = get_request_status(context.request_id)
    print("result \n {}".format(result))
    print("expected\n {}".format(expected))
    assert result == expected

@then('the request status API returns an error message')
def request_status_invalid_request_id(context):
    result = get_request_status(context.request_id)
    print(result)
    assert result['status'] == 'error'
    assert result['message'] == 'Invalid request_id'

@then('the request status API returns a missing query job message')
def null_job_request_status(context):
    with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
        mock_googleinterface().get_query_job_results.return_value = None

        result = get_request_status(context.request_id)
        print(result)
        assert result['status'] == 'error'
        assert result['message'] == 'No such request - Missing query job.'

@then('the request status API returns a query still running message')
def null_job_request_status(context):
    googleinterface = context.googleinterface
    with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
        mock_googleinterface().get_query_job_results = MagicMock()
        mock_googleinterface().get_query_job_results().complete = False

        result = get_request_status(context.request_id)
        print(result)
        assert result['status'] == 'running'
        assert result['message'] == 'Query job is running.'

@then('the request status API returns a missing extraction job message')
def null_job_request_status(context):
    googleinterface = context.googleinterface
    with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
        mock_googleinterface().get_query_job_results = MagicMock()
        mock_googleinterface().get_query_job_results().errors = None
        mock_googleinterface().get_extract_job.return_value = None

        result = get_request_status(context.request_id)
        print(result)
        assert result['status'] == 'error'
        assert result['message'] == 'Extraction not found. Might retry.'

@then('the request status API returns an extraction still running message')
def null_job_request_status(context):
    googleinterface = context.googleinterface
    with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
        mock_googleinterface().get_query_job_results = MagicMock()
        mock_googleinterface().get_query_job_results().errors = None
        mock_googleinterface().get_extract_job.return_value = MagicMock()

        result = get_request_status(context.request_id)
        print(result)
        assert result['status'] == 'running'
        assert result['message'] == 'Extraction job is running.'
