import sys
sys.path.append('../../')

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
