Feature: Job Status
    """
      Retrieve job status from BigQuery
    """

    Scenario: Successfully retrieves a request by id
      Given a successful request id
      When I receive a successful query job result
      and I receive a successful extract job result
      Then the API returns a complete request status