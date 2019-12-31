# Tests bigclam_interactions.py

Feature:

    Scenario: User runs an invalid run_bigclam_g2g_query
        Given a bigclam run_bigclam_g2g_query with invalid request
        Then a json error message is returned

    Scenario: User submits a valid run_bigclam_g2g_query
        Given a valid run_bigclam_g2g_query
        Then no json error messages are returned

    Scenario: User runs an invalid run_bigclam_g2d_query
        Given a bigclam run_bigclam_g2d_query with invalid request
        Then a json error message is returned

    Scenario: User submits a valid run_bigclam_g2d_query
        Given a valid run_bigclam_g2d_query
        Then no json error messages are returned

