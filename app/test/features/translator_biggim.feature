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
          | table                   |   fake_table              |
          | restriction boolean     |   BioGRID_Inter,None      |
          | average columns         |   None                    |

    Scenario: User submits a valid request
        Given a valid biggim request is provided
        Then no error messages are returned from biggim
