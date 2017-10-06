from app.database import db
from app.database.models import TestModel
from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET

def test_business(data):
    return "test_business"


def list_files(request_id):
    pass

def get_request_status(request_id):
    gi = GoogleInterface()
    query_job_id = gi.get_query_job_id(request_id)
    glogger.debug("Searching for %s query job" % (query_job_id,))
    query_job = gi.get_job(query_job_id)
    result = {'request_id':request_id}
    if query_job is None:
        result['status'] = 'error'
        result['message'] = 'No such request'
    elif query_job.state != 'DONE':
        result['status'] = 'running'
        glogger.debug("%s query job still running" % (extract_job_id,))
        return result
    else:
        extract_job_id = gi.get_extract_job_id(request_id)
        glogger.debug("Searching for %s extract job" % (extract_job_id,))
        extract_job = gi.get_job(extract_job_id)
        if extract_job is None:
            result['status'] = 'error'
            result['message'] = 'No such request'
            glogger.debug("Extract job %s not found." % (extract_job_id,))
        elif extract_job.state != 'DONE':
            result['status'] = 'running'
        else:
            result['request_uri'] = gi.get_urls( request_id ) 
            result['status'] = 'complete'
    return result

def run_query(query):
    gi = GoogleInterface()
    request_id = gi.query(query)
    return request_id


def extract_callback(extract_job):
    """
    Callback function that runs after a query has been run and the result has
    been written to google cloud storage.
    """
    try:
        gi = GoogleInterface()
        glogger.debug("Extract job %s complete." % (extract_job.name))
        if extract_job.errors is None:
            output_files = gi.list_blobs(prefix=gi.get_job_id(extract_job.name))
            glogger.debug("%s" % (str(output_files)))
            if len(output_files) > 0:
                map(lambda x: x.make_public(), output_files)
                for x in output_files:
                    glogger.debug('Made public %s', x.name)
            else:
                glogger.exception("Error extracting %s", (extract_job.name))
        else:
            glogger.exception("Error extracting %s", (extract_job.name))
    except:
        glogger.exception("Error in extract_callback for %s", (extract_job.name))


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

    def get_job_id(self, compound_id):
        return compound_id[3:]

    def query(self, query, bucket_name=BUCKET):
        glogger.debug("Running query")
        request_id = str(uuid.uuid4())

        query_job = self.bq_client.run_async_query(self.get_query_job_id(request_id), query)
        query_job.begin()
        # Print the results.
        destination_table = query_job.destination

        extract_job = self.bq_client.extract_table_to_storage(
            self.get_extract_job_id(request_id), destination_table,
            'gs://%s/%s*.csv' % (bucket_name, request_id))
        extract_job.destination_format = 'CSV'

        extract_job.begin()
        extract_job.add_done_callback(extract_callback)
        return request_id

    def list_blobs(self, bucket_name=BUCKET, prefix=''):
        glogger.debug("List blobs")
        bucket = self.gcs_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        my_blobs = [b for b in blobs if b.name.find(prefix) > -1]
        glogger.debug("Found %i blobs with %s prefix" % (len(my_blobs), prefix))
        return my_blobs

    def get_job(self, job_id):
        for j in self.bq_client.list_jobs():
            if j.name == job_id:
                return j
        return None

    def get_urls(self, job_id):
        job = self.get_job(self.get_extract_job_id(job_id))

        if job.state == u'DONE':
            return map(lambda x: x.public_url, self.list_blobs(prefix=job_id))
        else:
            raise Exception("Job %s is not done" % (job_id))



