import sys
sys.path.append('../../')

from behave import *

@given('a valid list of genes')
def step_valid_gene_list(context):
  context.genes = ['TCOF1', 'KLK3']

@given('a valid query of "{query_type}"')
def step_valid_query_type(context, query_type):
  context.query_type = query_type

@given('no query_type')
def step_no_query_type(context):
  context.query_type = None

@when(u'{who} try to {what}')
def step_impl(context, who, what):
  """
  For use when the step should expect an exception.
  Name the step "XXXX try to YYYY" and it will call a
  when step named "XXXX YYYY" with the exception in context
  """
  try:
      step_name = u'when {} {}'.format(who, what)
      context.execute_steps(step_name)
      context.exception=None
  except Exception as e:
      context.exception = e

@then('there should be an exception with value "{value}"')
def step_exception_value(context, value):
  print("Looking for this in exception message:", value)
  print("exception message", str(context.exception))
  assert value in str(context.exception)

@then('a json error message is returned')
def json_error_message(context):
    assert context.json_response['status'] == 'error'
    assert context.json_response['message'] is not None

@then('no json error messages are returned')
def json_error_message(context):
    assert context.json_response['status'] == 'submitted'
    assert 'message' not in context.json_response
    assert context.json_response['request_id'] is not None
