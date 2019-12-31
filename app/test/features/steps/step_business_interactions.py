import sys
sys.path.append('../../')

from behave import given, when, then
from mock import patch

from app.api.bigquery.business_interactions import get_request_status

@given('a successful request id')
def successful_request(context):
  context.request_id = "77dae546-b1e4-433e-9b47-4de68fe35686"

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

