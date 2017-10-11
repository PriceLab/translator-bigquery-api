from app.database import db
from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging
import time
import numpy as np

glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET
PROJECT = settings.BIGQUERY_PROJECT

def not_found_error(job):
    return len([x for x in job.errors if 'notFound' in x.values()]) > 0

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
        return compound_id.split('-')[-1]

    def query(self, query, bucket_name=BUCKET):
        glogger.debug("Running query")
        request_id = str(uuid.uuid4())
        query_job = self.bq_client.run_async_query(self.get_query_job_id(request_id), query)
        query_job.begin()
        # Print the results.
        destination_table = query_job.destination
        glogger.debug("%s" % (destination_table,))
        self.extract_job(request_id, destination_table)
        return request_id
    
    def extract_job(self, request_id, destination_table, trial=0):
        extract_job = self.bq_client.extract_table_to_storage(
            self.get_extract_job_id(request_id, trial=trial), destination_table,
            'gs://%s/%s*.csv' % (settings.BIGQUERY_BUCKET, request_id))
        extract_job.destination_format = 'CSV'
        extract_job.begin()
        extract_job.add_done_callback(extract_callback)
        

    def list_blobs(self, bucket_name=BUCKET, prefix=''):
        glogger.debug("List blobs")
        bucket = self.gcs_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        my_blobs = [b for b in blobs if b.name.find(prefix) > -1]
        glogger.debug("Found %i blobs with %s prefix" % (len(my_blobs), prefix))
        return my_blobs

    def get_extract_job(self, request_id):
        ej = [j for j in self.bq_client.list_jobs() if j.name.find(request_id) > -1 and j.name.find('ej') > -1]
        jobs = sorted(ej, key=lambda x: x.name)
        return jobs[-1]
    
    def get_query_job(self, request_id):
        ej = [j for j in self.bq_client.list_jobs() if j.name.find(request_id) > -1 and j.name.find('bq') > -1]
        jobs = sorted(ej, key=lambda x: x.name)
        return jobs[-1]
    
    def get_job(self, job_id):
        for j in self.bq_client.list_jobs():
            if j.name == job_id:
                return j
        return None

    def get_urls(self, request_id):
        job = self.get_extract_job(request_id)
        
        if job is None:
            glogger.debug("No job for %s" % (request_id, ))
            raise Exception("No such job.")
        if job.state == u'DONE' and job.errors is None:
            glogger.debug("Getting urls for extract job %s" % job.name)
            return map(lambda x: x.public_url, self.list_blobs(prefix=request_id))
        elif job.errors is not None:
            glogger.warning("Error on extract job")
        else:
            raise Exception("Job %s is not done" % (request_id))


class QueryBuilder:
    """Generates and validates a provided query"""
    def __init__(self, table=settings.BIGQUERY_DEFAULT_TABLE, 
            columns=[], 
            genes_from=[], 
            genes_to=[],
            restriction_gt=[], 
            restriction_lt=[],
            error_messages=[]):
        self._project = settings.BIGQUERY_PROJECT
        self._dataset = settings.BIGQUERY_DATASET
        self._table = table
        self._columns = columns
        self._genes_from = genes_from
        self._genes_to = genes_to
        self._restriction_gt = restriction_gt
        self._restriction_lt = restriction_lt
        self._preparsing_errors = error_messages

    def invalid_table(self):
        if not self.get_table().exists():
            return ["Bad table: %s" % (self._table)]
        else:
            return []

    def invalid_columns(self):
        tbl_columns = self.get_column_names()
        missing_columns = ["Bad column: %s" % c for c in self._columns if c not in tbl_columns]
        return missing_columns

    def invalid_genes(self):
        bad_genes = []
        for g in self._genes_from:
            try:
                i = int(g)
            except:
                bad_genes.append(g)
        for g in self._genes_to:
            try:
                i = int(g)
            except:
                bad_genes.append(g)
        if len(bad_genes):
            return ["Bad gene: %s" % (g) for g in bad_genes]
        else:
            return []

    def invalid_restrictions(self):
        invalid_restriction = []
        tbl_columns = self.get_column_names()
        for column, value in self._restriction_gt:
            if column not in tbl_columns:
                invalid_restriction.append("Bad column in restriction: %s > %s" % (column, value ))
            try:
                i = float(value)
            except:
                invalid_restriction.append("Bad value in restriction: %s > %s" % (column, value ))
        for column, value in self._restriction_lt:
            if column not in tbl_columns:
                invalid_restriction.append("Bad column in restriction: %s < %s" % (column, value ))
            try:
                i = float(value)
            except:
                invalid_restriction.append("Bad value in restriction: %s < %s" % (column, value ))
        return invalid_restriction

    def validate_query(self):
        it = self.invalid_table()
        ic = self.invalid_columns()
        ig = self.invalid_genes()
        ir = self.invalid_restrictions()

        errors = self._preparsing_errors + it + ic + ir + ig
        return errors

    def generate_query(self):
        sbase = ["GPID", "Gene1", "Gene2"]
        if len(self._columns):
            SELECT = 'SELECT ' + ', '.join(sbase + self._columns)
        else:
            SELECT = 'SELECT * '
        FROM = "FROM [%s:%s.%s]" % (self._project, self._dataset, self._table)
        WHERE = []
        for column, value in self._restriction_gt:
            if column.find('Pvalue') > -1:
                value = -1*np.log(float(value))
            else:
                value = float(value)
            line = " %s > %.5f " % (column, float(value))
            WHERE.append(line)
        for column, value in self._restriction_lt:
            if column.find('Pvalue') > -1:
                value = -1*np.log(float(value))
            else:
                value = float(value)
            line = " %s < %.5f " % (column, value)
            WHERE.append(line)
        if len(self._genes_to):
            gf = ','.join(self._genes_from)
            gt = ','.join(self._genes_to)
            WHERE.append("((Gene1 IN (%s) AND Gene2 IN (%s)) OR (Gene1 IN (%s) AND Gene2 IN (%s)))" % (gf, gt, gt, gf))
        elif len(self._genes_from):
            gf = ','.join(self._genes_from)
            WHERE.append("((Gene1 IN (%s) OR Gene2 IN (%s)))" % (gf, gf))
        if len(WHERE):
            WHERE = "WHERE " + ' AND '.join(WHERE)
        else:
            WHERE = ''
        query = '\n'.join([SELECT, FROM, WHERE])
        debug = " LIMIT 100"
        query += debug
        glogger.debug("Generated query [%s]" % (query))
        return query
    
    def get_table(self):
        gi = GoogleInterface()
        ds = gi.bq_client.dataset(self._dataset)
        tbl = ds.table(self._table)
        return tbl
    
    def get_column_names(self):
        tbl = self.get_table()
        if tbl.exists():
            tbl.reload()
            return [sc.name for sc in tbl.schema]
        else:
            glogger.exception("No such table [%s.%s]" % (self._project, self._table))
            raise Exception("No such table [%s.%s]" % (self._project, self._table))

    @classmethod
    def from_request(cls, request):
        """Generates QueryGenerator object from request"""
        def parse_list(gstr):
            return map(lambda x: x.strip(), gstr.split(','))

        def parse_restrictions(rstr):
            rlist = parse_list(rstr)
            if len(rlist) < 2 or len(rlist) % 2 != 0:
                raise Exception("Bad restriction")
            restrictions = []
            for i in range(len(rlist)/2):
                restrictions.append((rlist[2*i], rlist[2*i+1]))
            return restrictions


        error_messages = []
        rj = request.json
        args = {}
        if 'ids1' in rj:
            args['genes_from'] = parse_list(rj['ids1'])
        if 'ids2' in rj:
            args['genes_to'] = parse_list(rj['ids2'])
        if 'columns' in rj:
            args['columns'] = parse_list(rj['columns'])
        if 'table' in rj:
            args['table'] = rj['table']
        if 'restriction_lt' in rj:
            try:
                args['restriction_lt'] = parse_restrictions(rj['restriction_lt'])
            except:
                error_messages += ['Unparseable restriction_lt [%s]' % (rj['restriction_lt'],)]
        if 'restriction_gt' in rj:
            try:
                args['restriction_gt'] = parse_restrictions(rj['restriction_gt'])
            except:
                error_messages += ['Unparseable restriction_gt [%s]' % (rj['restriction_gt'],)]
        if len(error_messages) > 0:
            args['error_messages'] = error_messages

        glogger.debug("Args object.[%s]" % (str(args),))
        return cls(**args)
