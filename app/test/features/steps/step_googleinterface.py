import uuid
from behave import given, when, then
from mock import Mock, patch
from google.cloud.bigquery.query import QueryResults
from google.cloud.bigquery.client import Client

from app.api.bigquery.querytools import GoogleInterface


"""
This is a series of steps that mock the GoogleInterface class to return specific values
"""

def successful_run_async_query(context):
  """ For querytools.py:run_async_query """
  mock_bq_client = Mock()
  mock_bq_client.run_async_query.return_value = {
    "status": "submitted",
    "request_id": "77dae546-b1e4-433e-9b47-4de68fe35686"
  }
  context.bq_client = mock_bq_client

@when('I receive a successful query job result')
def successful_get_query_results(context):
  """ For querytools.py:get_query_job_results """
  if 'googleinterface' in context:
    print("FOUND successful_get_query_results MOCK")
    googleinterface = context.googleinterface
  else:
    googleinterface = Mock()

  print("mock bq_client?", googleinterface.bq_client)
  qr = QueryResults.from_api_repr({
    u'kind': u'bigquery#getQueryResultsResponse',
    u'jobReference': {
      u'projectId': u'isb-cgc-04-0010',
      u'location': u'US',
      u'jobId': u'bq-0-77dae546-b1e4-433e-9b47-4de68fe35686'
    },
    u'jobComplete': True,
    u'totalRows': u'100',
    u'totalBytesProcessed': u'1107667335',
    u'cacheHit': False,
    u'etag': u'k+lOdTYrkQpkLxTfxPyVCg==',
    u'schema': {
      u'fields': [
        {u'type': u'INTEGER', u'name': u'Gene1', u'mode': u'NULLABLE'},
        {u'type': u'STRING', u'name': u'Symbol1', u'mode': u'NULLABLE'},
        {u'type': u'INTEGER', u'name': u'Gene2', u'mode': u'NULLABLE'},
        {u'type': u'STRING', u'name': u'Symbol2', u'mode': u'NULLABLE'},
        {u'type': u'FLOAT', u'name': u'maxCorr', u'mode': u'NULLABLE'},
        {u'type': u'FLOAT', u'name': u'minCorr', u'mode': u'NULLABLE'},
        {u'type': u'FLOAT', u'name': u'aveCorr', u'mode': u'NULLABLE'}
      ]
    }
  }, googleinterface.bq_client)
  print("successful_query_results {}".format(qr))
  googleinterface.get_query_job_results.return_value = qr
  context.googleinterface = googleinterface

@when('I receive a successful extract job result')
def successful_get_list_jobs(context):
  """ For querytools.py get_extract_job"""
  if 'googleinterface' in context:
    print("FOUND successful_get_list_jobs MOCK")
    googleinterface = context.googleinterface
  else:
    googleinterface = Mock()

  print("RETURNING GET EXTRACT JOB")
  # Uses the current credentials to create a client that can parse the
  # saved response object into a Job.
  gi = GoogleInterface()
  job = gi.bq_client.job_from_resource({
    u'status': {u'state': u'DONE'},
    u'kind': u'bigquery#job',
    u'statistics':
      {
        u'totalSlotMs': u'119',
        u'completionRatio': 1,
        u'reservationUsage': [{u'name': u'default-pipeline', u'slotMs': u'119'}],
        u'creationTime': u'1577409449226',
        u'reservationId': u'default-pipeline',
        u'startTime': u'1577409449313',
        u'endTime': u'1577409450148',
        u'extract': {u'destinationUriFileCounts': [u'1'], u'inputBytes': u'0'}
      },
    u'jobReference': {
      u'projectId': u'isb-cgc-04-0010',
      u'location': u'US',
      u'jobId': u'ej-0-77dae546-b1e4-433e-9b47-4de68fe35686'
    },
    u'state': u'DONE',
    u'configuration': {
      u'extract': {
        u'destinationUri': u'gs://ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686*.csv', u'destinationFormat': u'CSV',
        u'destinationUris': [u'gs://ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686*.csv'],
        u'sourceTable': {
          u'projectId': u'isb-cgc-04-0010',
          u'tableId': u'anon33382df3f2205c9dd850899eaac186331c305464',
          u'datasetId': u'_95b820e413a4ca33e0c246679442be45d0004cfb'
        }
      },
      u'jobType': u'EXTRACT'
    },
    u'id': u'isb-cgc-04-0010:US.ej-0-77dae546-b1e4-433e-9b47-4de68fe35686',
    u'user_email': u'translator-bigquery@isb-cgc-04-0010.iam.gserviceaccount.com'
  })
  print("\nJOB IS {}\n".format(job))
  googleinterface.get_extract_job.return_value = job
  context.googleinterface = googleinterface

@when('I receive a successful list_blobs result')
def successful_list_blobs(context):
  if 'googleinterface' in context:
    print("FOUND successful_get_urls MOCK")
    googleinterface = context.googleinterface
  else:
    googleinterface = Mock()

  blob = Mock()
  blob.size = 4260
  googleinterface.list_blobs.return_value = [blob]
  context.googleinterface = googleinterface


@when('I receive a successful get_urls result')
def successful_get_urls(context):
  if 'googleinterface' in context:
    print("FOUND successful_get_list_jobs MOCK")
    googleinterface = context.googleinterface
  else:
    googleinterface = Mock()

  googleinterface.get_urls.return_value = [
    "https://storage.googleapis.com/ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv"
  ]
  context.googleinterface = googleinterface

def successful_get_list_jobs(context):
  """ For querytools.py bq_client.list_jobs"""
  if 'bq_client' in context:
    print("FOUND MOCK")
    mock_bq_client = context.bq_client
  else:
    mock_bq_client = Mock()

  mock_bq_client.list_jobs.return_value = [
    {
      u'status': {u'state': u'DONE'},
      u'kind': u'bigquery#job',
      u'statistics':
        {
          u'totalSlotMs': u'119',
          u'completionRatio': 1,
          u'reservationUsage': [{u'name': u'default-pipeline', u'slotMs': u'119'}],
          u'creationTime': u'1577409449226',
          u'reservationId': u'default-pipeline',
          u'startTime': u'1577409449313',
          u'endTime': u'1577409450148',
          u'extract': {u'destinationUriFileCounts': [u'1'], u'inputBytes': u'0'}
        },
      u'jobReference': {
        u'projectId': u'isb-cgc-04-0010',
        u'location': u'US',
        u'jobId': u'ej-0-77dae546-b1e4-433e-9b47-4de68fe35686'
      },
      u'state': u'DONE',
      u'configuration': {
        u'extract': {
          u'destinationUri': u'gs://ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686*.csv', u'destinationFormat': u'CSV',
          u'destinationUris': [u'gs://ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686*.csv'],
          u'sourceTable': {
            u'projectId': u'isb-cgc-04-0010',
            u'tableId': u'anon33382df3f2205c9dd850899eaac186331c305464',
            u'datasetId': u'_95b820e413a4ca33e0c246679442be45d0004cfb'
          }
        },
        u'jobType': u'EXTRACT'
      },
      u'id': u'isb-cgc-04-0010:US.ej-0-77dae546-b1e4-433e-9b47-4de68fe35686',
      u'user_email': u'translator-bigquery@isb-cgc-04-0010.iam.gserviceaccount.com'
    },
    {
      u'status': {u'state': u'DONE'},
      u'kind': u'bigquery#job',
      u'statistics': {
        u'totalSlotMs': u'61532', u'creationTime': u'1577409447105', u'totalBytesProcessed': u'1107667335', u'startTime': u'1577409447387',
        u'query': {
          u'totalSlotMs': u'61532',
          u'queryPlan': [
            {
              u'readMsMax': u'92', u'computeMsMax': u'54', u'waitMsAvg': u'1', u'id': u'0', u'endMs': u'1577409447748', u'waitMsMax': u'1',
              u'startMs': u'1577409447591', u'waitRatioMax': 0.0027624309392265192, u'readRatioAvg': 0.2541436464088398, u'parallelInputs': u'1',
              u'recordsRead': u'45740', u'computeRatioAvg': 0.14917127071823205, u'writeMsAvg': u'24', u'status': u'COMPLETE',
              u'writeMsMax': u'24', u'computeMsAvg': u'54', u'shuffleOutputBytesSpilled': u'0', u'slotMs': u'164',
              u'writeRatioMax': 0.06629834254143646, u'readMsAvg': u'92', u'waitRatioAvg': 0.0027624309392265192,
              u'completedParallelInputs': u'1', u'computeRatioMax': 0.14917127071823205, u'name': u'S00: Input', u'shuffleOutputBytes': u'798926',
              u'recordsWritten': u'38631', u'readRatioMax': 0.2541436464088398,
              u'steps': [
                {u'kind': u'READ', u'substeps': [u'$1:Approved_Symbol, $2:Entrez_Gene_ID', u'FROM isb-cgc.genome_reference.genenames_mapping']},
                {u'kind': u'COMPUTE', u'substeps': [u'$40 := CAST($2 AS INT64)']},
                {u'kind': u'WRITE', u'substeps': [u'$1, $40', u'TO __stage00_output', u'BY HASH($40)']}
              ],
              u'writeRatioAvg': 0.06629834254143646
            }
          ],
          u'estimatedBytesProcessed': u'1107667335',
          u'timeline': [
            {u'totalSlotMs': u'46999', u'activeUnits': u'69', u'completedUnits': u'301', u'elapsedMs': u'706', u'pendingUnits': u'69'},
            {u'totalSlotMs': u'61532', u'activeUnits': u'69', u'completedUnits': u'370', u'elapsedMs': u'1040', u'pendingUnits': u'0'}
          ],
          u'statementType': u'SELECT', u'totalBytesBilled': u'1108344832', u'totalPartitionsProcessed': u'0', u'totalBytesProcessed': u'1107667335',
          u'cacheHit': False, u'billingTier': 1,
          u'referencedTables': [
            {u'projectId': u'isb-cgc', u'tableId': u'genenames_mapping', u'datasetId': u'genome_reference'},
            {u'projectId': u'isb-cgc-04-0010', u'tableId': u'BigGIM_70_v1', u'datasetId': u'NTTB_BigGIM'}
          ]
        },
        u'endTime': u'1577409448454'
      },
      u'jobReference': {u'projectId': u'isb-cgc-04-0010', u'location': u'US', u'jobId': u'bq-0-77dae546-b1e4-433e-9b47-4de68fe35686'},
      u'state': u'DONE',
      u'configuration': {
        u'query': {
          u'useLegacySql': False,
          u'destinationTable': {
            u'projectId': u'isb-cgc-04-0010',
            u'tableId': u'anon33382df3f2205c9dd850899eaac186331c305464',
            u'datasetId': u'_95b820e413a4ca33e0c246679442be45d0004cfb'
          },
          u'priority': u'INTERACTIVE',
          u'writeDisposition': u'WRITE_TRUNCATE',
          u'createDisposition': u'CREATE_IF_NEEDED',
          u'query': u'\n        WITH \n        t1 AS (\n        SELECT GPID, Gene1, Gene2, GREATEST(TCGA_BLCA_Correlation) AS maxCorr, \n            LEAST(TCGA_BLCA_Correlation) AS minCorr, \n            (TCGA_BLCA_Correlation)/(IF(TCGA_BLCA_Correlation IS NULL, 0, 1)) as aveCorr \n            \n        FROM `isb-cgc-04-0010.NTTB_BigGIM.BigGIM_70_v1` \n        WHERE (Gene1=5111 OR Gene2=5111) \n        ),\n        j1 AS (\n        SELECT Gene1, b.Approved_Symbol AS Symbol1, Gene2, maxCorr, minCorr, aveCorr\n        FROM t1 a JOIN `isb-cgc.genome_reference.genenames_mapping` b \n            ON a.Gene1=CAST(b.Entrez_Gene_ID AS INT64)),\n        j2 AS (\n        SELECT Gene1, Symbol1, Gene2, b.Approved_Symbol AS Symbol2, maxCorr, minCorr, aveCorr\n        FROM j1 a JOIN `isb-cgc.genome_reference.genenames_mapping` b \n            ON a.Gene2=CAST(b.Entrez_Gene_ID AS INT64)  \n        )\n        SELECT Gene1, Symbol1, Gene2, Symbol2, maxCorr, minCorr, aveCorr\n        FROM j2\n        WHERE not IS_NAN(maxCorr)\n        ORDER BY ABS(aveCorr) DESC\n        LIMIT 100\n        '
        },
        u'jobType': u'QUERY'
      },
      u'id': u'isb-cgc-04-0010:US.bq-0-77dae546-b1e4-433e-9b47-4de68fe35686',
      u'user_email': u'translator-bigquery@isb-cgc-04-0010.iam.gserviceaccount.com'
    }
  ]
  context.bq_client = mock_bq_client

def successful_storage_results(context):
  """ for use in querytools.py:list_blobs """

  mock_bucket.list_blobs.return_value = {
    u'items': [
      {
        u'kind': u'storage#object',
        u'contentType': u'application/octet-stream',
        u'name': u'77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv',
        u'etag': u'CLbKp4/U1OYCEBE=',
        u'generation': u'1577409449682230',
        u'md5Hash': u'chmdgZEVFmxEE7baJxW5Yg==',
        u'bucket': u'ncats_bigquery_results',
        u'updated': u'2019-12-27T05:37:24.257Z',
        u'crc32c': u'FJux+Q==',
        u'metageneration': u'17',
        u'mediaLink': u'https://www.googleapis.com/download/storage/v1/b/ncats_bigquery_results/o/77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv?generation=1577409449682230&alt=media',
        u'timeStorageClassUpdated': u'2019-12-27T01:17:29.682Z',
        u'size': u'4264',
        u'timeCreated': u'2019-12-27T01:17:29.682Z',
        u'id': u'ncats_bigquery_results/77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv/1577409449682230',
        u'selfLink': u'https://www.googleapis.com/storage/v1/b/ncats_bigquery_results/o/77dae546-b1e4-433e-9b47-4de68fe35686000000000000.csv',
        u'storageClass': u'MULTI_REGIONAL'
      },
    ],
    u'kind': u'storage#objects'
  }
  context.bucket = mock_bucket

@given('I receive a successful query job submission')
def successful_query_submission_results(context):
  """ For bigclam_interactions.py:run_bigclam_g2g_query/run_bigclam_g2d_query """
  """ Needs to patch GoogleInterface.query to return a UUID4 """
  if 'googleinterface' in context:
    print("FOUND successful_query_submission_results MOCK")
    googleinterface = context.googleinterface
  else:
    googleinterface = Mock()

  googleinterface.query.return_value = str(uuid.uuid4())
  context.googleinterface = googleinterface