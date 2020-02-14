## translator_biggim.feature 
### Tests BigGIM at the top level API call. Scenarios include:
- User submits an empty request
- User submits request containing invalid parameters
- User submits a valid biggim request with all parameters is provided
- User submits a valid biggim request with less parameters

## translator_querytools.feature 
### Tests lower level functions related to BigGIM. Scenarios include:
- User submits an empty request
- User submits request containing invalid parameters
- User submits a valid request with all parameters is provided
- User submits a valid request with less parameters
- User submits a valid request with no gene or columns

## translator_bglite_business_interactions.feature: 
### Tests top level functions related to LittleGIM. Scenarios include:
- User runs an invalid run_bglite_gt2g_query with specific invalid arguments
- User runs an invalid run_bglite_gt2g_query
- User submits a valid run_bglite_gt2g_query

## translator_bigclam.feature
### Tests top level functions related to BigCLAM. Scenarios include:
- User submits an empty query
- User submits a query with invalid limit
- User submits bigclam query containing invalid parameters
- User submits a valid query
- User submits a list of genes and gets a string of genes for SQL replacement
- User quries get correct base queries
- User submits an invalid query type to base_query

## translator_bigclam_bi.feature
### Tests lower level functions related to BigCLAM. Scenarios include:
- User runs an invalid run_bigclam_g2g_query
- User submits a valid run_bigclam_g2g_query
- User runs an invalid run_bigclam_g2d_query
- User submits a valid run_bigclam_g2d_query

## translator_business_interactions.feature
### Tests interactions with BigQuery, including retreaving request IDs and job status. Scenarios include:
- Successfully retrieves a request by id
- User submits request status query containing invalid parameters
- User submits request that is a missing query job
- User submits request that is still running
- User submits request that is a missing extraction job
- User submits request that is still extracting
- User submits request and the query job fails 
