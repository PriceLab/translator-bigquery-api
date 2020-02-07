from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid
import logging
import time
from datetime import datetime, timedelta

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET
PROJECT = settings.BIGQUERY_PROJECT


def not_found_error(job):
    return len([x for x in job.errors if 'notFound' in x.values()]) > 0

def extract_result(query_job):
    glogger.debug("Extracting query job")
    gi = GoogleInterface()
    query_job_id = query_job.name
    job_id = gi.get_job_id( query_job_id )
    glogger.debug("Job id")
    destination_table = query_job.destination
    glogger.debug("Submitting extraction")
    gi.extract_job(job_id, destination_table, trial=0)
    glogger.debug("Extraction running")


def extract_callback(extract_job):
    """
    Callback function that runs after a query has been run and the result has
    been written to google cloud storage.
    """
    def make_files_public(extract_job):
        """Need to make the files public for download."""
        gi = GoogleInterface()
        output_files = gi.list_blobs(prefix=gi.get_job_id(extract_job.name))
        glogger.debug("%s generated %s" % (extract_job.name,
                                           ','.join(map(lambda x: x.name, output_files))))
        if len(output_files) > 0:
            map(lambda x: x.make_public(), output_files)
            for x in output_files:
                glogger.debug('Made public %s', x.name)
        else:
            glogger.exception("No files generated error extracting %s" % (extract_job.name))

    def rerun_extract(extract_job):
        """Not found error means retry extraction"""
        gi = GoogleInterface()
        glogger.warning("Not found error while extracting %s", (extract_job.name))
        ejs = extract_job.name.split('-')
        trial = ejs[1]
        rid = '-'.join(ejs[2:])
        #see if query completed
        qj = gi.get_query_job(rid)
        if qj is not None and qj.errors is None and int(trial) < 5:
            glogger.warning("Query job %s is fine. Retrying extraction %s" % (qj.name, extract_job.name))
            time.sleep(int(trial)**2 + 5)
            return gi.extract_job(rid, qj.destination, trial=int(trial) + 1)
        elif int(trial) >= 5:
            glogger.warning("Error on extraction %s, no more retries" %(extract_job.name))
        else:
            glogger.exception("Error on request %s and extracting %s" % (rid, extract_job.name))
    try:
        glogger.debug("Extract job %s complete." % (extract_job.name))
        if extract_job.errors is None:
            make_files_public(extract_job)
        elif not_found_error(extract_job):
            rerun_extract(extract_job)
        else:
            glogger.exception("Unrecoverable error on extracting %s. %s" % (extract_job.name, str(extract_job.errors)))
    except:
        glogger.exception("Exceptioon in extract_callback for %s" % (extract_job.name))


class GoogleInterface:
    """
    This is a simplified class for querying bigquery.
    """
    def __init__(self, key=KEY):
        self._key = key
        self._allow_big_results = True

    @property
    def bq_client(self):
        return  bigquery.Client.from_service_account_json(self._key)

    @property
    def gcs_client(self):
        return storage.Client.from_service_account_json(self._key)

    def get_query_job_id(self, request_id, trial=0):
        return "bq-%i-%s" % ( trial, request_id,)

    def get_extract_job_id(self, request_id, trial=0):
        return "ej-%i-%s" % ( trial, request_id)

    def get_job_id(self, compound_id):
        return '-'.join(compound_id.split('-')[2:])

    def get_temp_table_name(self, request_id):
        return "_temp_%s" % (request_id.replace('-','_'))

    def query(self, query, bucket_name=BUCKET):
        glogger.debug("Running query")
        request_id = str(uuid.uuid4())
        query_job = self.bq_client.run_async_query(self.get_query_job_id(request_id), query)
        query_job.use_legacy_sql = False
        glogger.debug("Starting query job")
        if self._allow_big_results:
            glogger.debug("Creating temp table for large results")
            ds =  self.bq_client.dataset(settings.BIGQUERY_DATASET)
            table = ds.table(name=self.get_temp_table_name(request_id))
            table.expires = datetime.now() + timedelta(hours=1)
            table.create()
            query_job.write_disposition = 'WRITE_TRUNCATE'
            query_job.destination_table = table
        query_job.begin()

        query_job.add_done_callback(extract_result)
        return request_id

    def extract_job(self, request_id, destination_table, trial=0):
        glogger.debug("Setting up extract job")
        extract_job = self.bq_client.extract_table_to_storage(
            self.get_extract_job_id(request_id, trial=trial), destination_table,
            'gs://%s/%s*.csv' % (settings.BIGQUERY_BUCKET, request_id))
        extract_job.destination_format = 'CSV'
        glogger.debug("Setting up extract job")
        extract_job.begin()
        glogger.debug("Adding extract call_back")
        extract_job.add_done_callback(extract_callback)
        glogger.debug("Leaving extract job")

    def list_blobs(self, bucket_name=BUCKET, prefix=''):
        glogger.debug("List blobs")
        bucket = self.gcs_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        my_blobs = [b for b in blobs if b.name.find(prefix) > -1]
        glogger.debug("Found %i blobs with %s prefix" % (len(my_blobs), prefix))
        return my_blobs

    def get_extract_job(self, request_id):
        # TODO: improve this. it was really slowing things down
        # I made a bandaid fix here
        # we should upgrade the api and restrict the listjob query
        # but for now this should speed things up
        for j in self.bq_client.list_jobs():
            if j.name.find(request_id) > -1 and j.name.find('ej') > -1:
                return j
        return None

    def get_query_job_results(self, request_id):
        ## See above for notes. This should be updated
        results = self.bq_client.get_query_results(request_id,
            project=settings.BIGQUERY_PROJECT)
        return results

    def get_job(self, job_id):
        for j in self.bq_client.list_jobs():
            if j.name == job_id:
                return j
        return None

    def get_urls(self, request_id):
        glogger.debug("Getting extract_job")
        job = self.get_extract_job(request_id)
        glogger.debug("Got extract_job")
        if job is None:
            glogger.debug("No job for %s" % (request_id, ))
            raise Exception("No such job.")
        if job.state == u'DONE' and job.errors is None:
            glogger.debug("Listing blobs")
            output_files = self.list_blobs(prefix=request_id)
            glogger.debug("Making blobs public")
            for of in output_files:
                glogger.debug("Making %s public" % (of))
                of.make_public()
            glogger.debug("Getting urls for extract job %s" % job.name)
            return map(lambda x: x.public_url, output_files)
        elif job.errors is not None:
            glogger.warning("Error on extract job")
        else:
            raise Exception("Job %s is not done" % (request_id))
