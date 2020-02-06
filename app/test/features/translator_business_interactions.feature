Feature: Job Status
    """
      Retrieve job status from BigQuery
    """

    Scenario: Successfully retrieves a request by id
      Given a valid request id
      When I receive a successful query job result
      and I receive a successful extract job result
      and I receive a successful get_urls result
      and I receive a successful list_blobs result
      Then the API returns a complete request status

    Scenario Outline: User submits request status query containing invalid parameters
      Given an invalid request status query for "<request_id>"
      Then the request status API returns an invalid request ID error message

      Examples:
        | request_id                             |
        | "0a5c64ea-2832-494c-a91b-f1c6e5b565a4  |
        | test                                   |
        | 0a5c6555ea-2832-494c-a91b-f1c6e5b565a4 |

    Scenario: User submits request that is a missing query job
      Given a valid request id
      Then the request status API returns a missing query job message

    Scenario: User submits request that is still running
      Given a valid request id
      Then the request status API returns a query still running message

    Scenario: User submits request that is a missing extraction job
      Given a valid request id
      Then the request status API returns a missing extraction job message

    Scenario: User submits request that is still extracting
      Given a valid request id
      Then the request status API returns an extraction still running message

    Scenario: User submits request and the query job fails
      Given a valid request id
      Then the request status API returns an query job failed message
