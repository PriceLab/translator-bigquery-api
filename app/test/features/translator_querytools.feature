Feature: Parsing and checking input request
    Scenario: User submits an empty request
        Given an empty biggim request submitted
        Then no error messages are returned from biggim

    Scenario Outline: User submits request containing invalid parameters
        Given a biggim request with invalid "<argument type>" of "<argument>"
        Then a list of errors is returned from biggim

        Examples:
            | argument type           |   argument                |
            | genes                   |   FADS1, 139495           |
            | columns                 |   TCGA_GBM, TEST_COL      |
            | correlation threshold   |   TCGA_GBM_Correlation    |
            | pvalue threshold        |   TCGA_GBM_Pvalue         |
            | join type               |   add                     |
            | limits                  |   -1000                   |
            | limits                  |   Na                      |
            | table                   |   fake_table              |
            | restriction boolean     |   BioGRID_Inter,Na        |
            | restriction boolean     |   BioGRID_Inter           |
            | restriction_lt          |   BioGRID_Inter,True      |
            | restriction_lt          |   TEST_TEST,0.1           |
            | restriction_gt          |   BioGRID_Inter,True      |
            | restriction_gt          |   TEST_TEST,0.1           |
            | average columns         |   None                    |
            | table                   |   fake                    |

    Scenario: User submits a valid request with all parameters is provided
        Given a valid biggim request with all parameters is provided
        Then no error messages are returned from biggim

    Scenario: User submits a valid request with less parameters
        Given a valid biggim request with less parameters is provided
        Then no error messages are returned from biggim

    Scenario: User submits a valid request with no gene or columns
        Given a valid biggim request with no genes or columns is provided
        Then no error messages are returned from biggim