Feature: Submitting query to BigQuery
    Scenario: User submits an empty request
        Given an empty biggim request submitted
        Then the query gets a request id
        And the resulting status message says submitted

    Scenario Outline: User submits request containing invalid parameters
        Given a biggim request with invalid "<argument type>" of "<argument>"
        Then the resulting status message says errors with error messages

        Examples:
            | argument type           |   argument                |
            | genes                   |   FADS1, 139495           |
            | columns                 |   TCGA_GBM, TEST_COL      |
            | correlation threshold   |   TCGA_GBM_Correlation    |
            | pvalue threshold        |   TCGA_GBM_Pvalue         |
            | join type               |   add                     |
            | limits                  |   -1000                   |
            | table                   |   fake_table              |
            | restriction boolean     |   BioGRID_Inter,None      |
            | average columns         |   None                    |

    Scenario: User submits a valid request
        Given a valid biggim request is provided
        Then the query gets a request id
        And the resulting status message says submitted
