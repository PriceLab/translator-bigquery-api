import sys
sys.path.append('/')

from behave import *
from app.api.bigquery.bigclam import *

### Tests for fron_request
@given('an empty bigclam query submitted')
def step_submit_empty_query(context):
    empty_request = {}
    context.query = BCQueryBuilder.from_request(empty_request, 'g2g')

@given('a bigclam query with invalid limit parameter')
def step_submit_invalid_query(context):
    # query goes in the ids1
    request = {
      'ids1': 'TCOF1',
      'limit': 'TEST'
    }

    print(request)
    context.query = BCQueryBuilder.from_request(request, 'g2g')

@given('a bigclam query with invalid "{query_type}" for "{ids}"')
def step_submit_invalid_query(context, query_type, ids):
    # query goes in the ids1
    request = {
      'ids': ids
    }

    print(request)
    context.query = BCQueryBuilder.from_request(request, query_type)

@given('a valid bigclam query "{query_type}" for "{ids}" is provided')
def step_submit_valid_query(context, query_type, ids):
    valid_request = {
      'ids': ids,
      'limit': 100,
    }
    bcqb = BCQueryBuilder()
    context.query = BCQueryBuilder.from_request(valid_request, query_type)

### Misc Tests

@then('a SQL separated string is returned for strGlist')
def step_valid_sql_gene_string(context):
  genestring = BCQueryBuilder(context.genes).strGlist()
  expected = "'TCOF1','KLK3'"
  assert genestring == expected

@then('the "{query_function}" returns the correct SQL')
def step_valid_query_function_called(context, query_function):
  qb = BCQueryBuilder(context.genes, context.query_type)
  print(qb)
  print(query_function)
  expected = getattr(qb, query_function)()
  try:
    print(qb.__dict__)
    result = qb.base_query
  except Exception as e:
    import traceback
    print(e)
    print("found exception",traceback.print_exc())
  print(result)
  assert result == expected

@when(u"query_builder call base_query with invalid query_type")
def step_invalid_query_type_base_query(context):
  qb = BCQueryBuilder(context.genes, context.query_type)
  # throws an exception caught by try to step
  result = qb.base_query
