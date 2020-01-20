Feature: BGLite Business

    Scenario: User runs an invalid run_bglite_gt2g_query
        Given a configured sqlalchemy engine
        When a bglite run_bglite_gt2g_query with invalid request
        Then a json error message is returned

    Scenario: User submits a valid run_bglite_gt2g_query
        Given a configured sqlalchemy engine
        When I run a valid run_bglite_gt2g_query
        Then no json error messages are returned
        and reset sqlalchemy database