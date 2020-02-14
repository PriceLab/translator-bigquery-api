Feature: BGLite Business

    Scenario Outline: User runs an invalid run_bglite_gt2g_query with specific invalid arguments
        Given a configured sqlalchemy engine
        When a bglite run_bglite_gt2g_query with invalid "<argument type>" of "<argument>"
        Then a json error message is returned

        Examples:
            | argument type           |   argument                |
            | genes                   |   FADS1                   |
            | genes                   |   ''                      |
            | tissue                  |   INVALID_TISSUE          |
            | tissue                  |   ''                      |
            | minR                    |   na                      |
            | minR                    |   ''                      |
            | limit                   |   -1000                   |
            | table                   |   fake_table              |

    Scenario: User runs an invalid run_bglite_gt2g_query
        Given a configured sqlalchemy engine
        When a bglite run_bglite_gt2g_query with invalid parameter
        Then a json error message is returned


    Scenario: User submits a valid run_bglite_gt2g_query
        Given a configured sqlalchemy engine
        When I run a valid run_bglite_gt2g_query
        Then no json error messages are returned
        and reset sqlalchemy database
