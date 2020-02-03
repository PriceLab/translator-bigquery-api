import sys
sys.path.append('/')

from behave import given, when, then
from mock import patch
from google.cloud.bigquery.client import Client

from app.api.bigquery.business_interactions import run_bglite_gt2g_query
from app.main import app


@when('a bglite run_bglite_gt2g_query with invalid request')
def invalid_run_bglite_gt2g_query(context):
  """
  The invalid request still needs to have valid structure because the
  endpoint validation prevents bad structure
  """
  invalid_request = {'idfdsafsas': '5532'}
  with patch('app.api.bigquery.querytools.QueryBuilder.get_table') as mock_table:
      mock_table.exists().return_value = True

      with app.app_context():
        json_response = run_bglite_gt2g_query(invalid_request)
        context.json_response = json_response

@when('I run a valid run_bglite_gt2g_query')
def valid_run_bglite_gt2g_query(context):
  valid_request = {
    "tissue": 'whole_body',
    "limit": 100,
    "ids": "5111"
  }
  googleinterface = context.googleinterface

  with patch('app.api.bigquery.business_interactions.GoogleInterface') as mock_googleinterface:
    mock_googleinterface().query.return_value = googleinterface.query.return_value
    with patch('app.api.bigquery.querytools.QueryBuilder.get_table') as mock_table:
      mock_table.exists().return_value = True

      with app.app_context():
        json_response = run_bglite_gt2g_query(valid_request)
        context.json_response = json_response
