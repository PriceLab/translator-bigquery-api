# Tests api/bigclam.py:BCQueryBuilder

# This is 'valid' only because the endpoint does checking to make sure 'ids' is provided
# so there is no checking on from_request that genes are included
Feature: Parsing and checking input bigclam query
    Scenario: User submits an empty query
	   Given an empty bigclam query submitted
       Then no error messages are returned

     Scenario: User submits a query with invalid limit
        Given a bigclam query with invalid limit parameter
        Then a list of errors is returned

    Scenario Outline: User submits bigclam query containing invalid parameters
        Given a bigclam query with invalid "<query type>" for "<ids>"
        Then a list of errors is returned

        Examples:
          | query type          |   ids                |
          | blah                |   FADS1, 139495      |
          | g2d                 |   FADS1, 139495      |
          | g2g                 |   FADS1, 139495      |
          | g22d                |   FADS1, 139495      |

    Scenario Outline: User submits a valid query
        Given a valid bigclam query "<query type>" for "<ids>" is provided
        Then no error messages are returned

        Examples:
          | query type |  ids    |
          | g2d        |  TCOF1  |
          | g2g        |  TCOF1  |