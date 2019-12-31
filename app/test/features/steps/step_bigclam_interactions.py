import sys
sys.path.append('../../')

from behave import given, when, then
from mock import patch

from app.api.bigquery.bigclam_interactions import run_bigclam_g2d_query, run_bigclam_g2g_query

@given('a bigclam run_bigclam_g2g_query with invalid request')
def invalid_run_bigclam_g2g_query(context):
  """
  The invalid request still needs to have valid structure because the
  endpoint validation prevents bad structure
  """
  invalid_request = {'ids': '5532'}
  json_response = run_bigclam_g2g_query(invalid_request)
  context.json_response = json_response

@given('a valid run_bigclam_g2g_query')
def valid_run_bigclam_g2g_query(context):
  valid_request = {'ids': 'TCOF1'}
  json_response = run_bigclam_g2g_query(valid_request)
  context.json_response = json_response

@given('a bigclam run_bigclam_g2d_query with invalid request')
def invalid_run_bigclam_g2d_query(context):
  """
  The invalid request still needs to have valid structure because the
  endpoint validation prevents bad structure
  """
  invalid_request = {'ids': '5532'}
  json_response = run_bigclam_g2d_query(invalid_request)
  context.json_response = json_response

@given('a valid run_bigclam_g2d_query')
def valid_run_bigclam_g2d_query(context):
  valid_request = {'ids': 'TCOF1'}
  json_response = run_bigclam_g2d_query(valid_request)
  context.json_response = json_response
