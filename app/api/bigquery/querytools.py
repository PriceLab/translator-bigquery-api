from app.database import db
from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET
PROJECT = settings.BIGQUERY_PROJECT


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

class QueryBuilder:
    """Generates and validates a provided query"""
    def init(self, table=settings.BIGQUERY_DEFAULT_TABLE, 
            columns=[], 
            genes_from=[], 
            genes_to=[],
            restriction_gt=[], 
            restriction_lt=[]):
        self._project = settings.BIGQUERY_PROJECT
        self._table = table
        self._columns = columns
        self._genes_from = genes_from
        self._genes_to = genes_to
        self._restriction_gt = restriction_gt

    def invalid_table(self):
        self._project
        self._table
        return []

    def invalid_columns(self):
        self._project
        self._table
        self._columns
        return []


    def invalid_genes(self):
        self._genes_from
        self._genes_to
        return []

    def invalid_restrictions(self):
        self._restriction_gt
        self._restriction_lg
        return []

    def validate_query(self):
        it = self.invalid_table()
        ic = self.invalid_columns()
        ig = self.invalid_genes()
        ir = self.invalid_restrictions()

        errors = it + ic + ir + ig
        return errors

    def generate_query(self):
        sbase = ["Gene1","Gene2"]
        if len(columns):
            SELECT = 'SELECT ' + ', '.join(sbase + columns)
        else:
            SELECT = 'SELECT * '
        FROM = "FROM [%s.%s]" % (project, table)
        WHERE = []
        for column, value in restriction_gt:
            line = " %s > %.5f " % (column, value)
            WHERE.append(line)
        for column, value in restriction_lt:
            line = " %s < %.5f " % (column, value)
            WHERE.append(line)
        if len(genes_to):
            gf = ','.join(genes_from)
            gt = ','.join(genes_to)
            WHERE.append("((Gene1 IN (%s) AND Gene2 IN (%s)) OR (Gene1 IN (%s) AND Gene2 IN (%s)))" % (gf, gt, gt, gf))
        elif len(genes_from):
            WHERE.append("((Gene1 IN (%s) OR Gene2 IN (%s)))" % (gf, gf))
        if len(WHERE):
            WHERE = "WHERE " + ' AND '.join(WHERE)
        else:
            WHERE = ''
        query = '\n'.join([SELECT, FROM, WHERE])
        return query

    @classmethod
    def from_request(cls, request):
        """Generates QueryGenerator object from request"""
        return cls()


