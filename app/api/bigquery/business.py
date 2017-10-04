from app.database import db
from app.database.models import TestModel
from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging


def test_business(data):
    return "test_business"


def list_files(request_id):
    gi = GoogleInterface()
    query_job_id = gi.get_job(gi.get_query_job_id(data['request_id']))
    query_job = gi.get_job(query_job_id)
    result = {'request_id':request_id}
    if query_job.state != 'DONE':
        result['status'] = 'running'
        return result
    
    extract_job_id = gi.get_job(gi.get_extract_job_id(data['request_id']))
    extract_job = gi.get_job(extract_job_id)
    
    if extract_job.state != 'DONE':
        result['status'] = 'running'
        return result

    result['request_uri'] = gi.get_urls( request_id ) 
    result['status'] = 'complete'
    return result



glogger = logging.getLogger('GoogleInterface')
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET


def extract_callback(extract_job):
    gi = GoogleInterface()
    if extract_job.errors is None:
        glogger.debug("Extract job %s complete." % (extract_job.name))
        output_files = gi.list_blobs(prefix=extract_job.name)
        map(lambda x: x.make_public(), output_files)
        for x in output_files:
            glogger.debug('Made public %s', x)
    else:
        glogger.exception("Error extracting %s", (extract_job.name))



class GoogleInterface:
    """
    This is a simplified class for querying bigquery.
    """
    def __init__(self, key=KEY):
        self._key = key

    @property
    def bq_client(self):
        return  bigquery.Client.from_service_account_json(self._key)

    @property
    def gcs_client(self):
        return storage.Client.from_service_account_json(self._key)

    def get_query_job_id(self, request_id):
        return "bq-%s" % (request_id,)

    def get_extract_job_id(self, request_id):
        return "ej-%s" % (request_id,)

    def query(self, query, bucket_name=BUCKET):
        glogger.debug("Running query")
        request_id = str(uuid.uuid4())

        query_job = self.bq_client.run_async_query(self.get_query_job_id, query)
        query_job.begin()
        # Print the results.
        destination_table = query_job.destination

        extract_job = client.extract_table_to_storage(
            self.get_extract_job_id(request_id), destination_table,
            'gs://%s/%s*.csv' % (bucket_name, request_id))
        extract_job.destination_format = 'CSV'

        extract_job.begin()
        extract_job.add_done_callback(dumb_callback)
        return {'request_id': request_id}

    def list_blobs(self, bucket_name=BUCKET, prefix=''):
        bucket = self.gcs_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        return [b for b in blobs if b.name.find(prefix) > -1]

    def get_job(self, job_id):
        for j in self.bq_client.list_jobs():
            if j.name == job_id:
                return j

    def get_urls(self, job_id):
        job = self.get_job(job_id)
        if job.state == u'DONE':
            return map(lambda x: x.public_url, self.list_blobs(prefix=job_id))
        else:
            raise Exception("Job %s is not done" % (job_id))


