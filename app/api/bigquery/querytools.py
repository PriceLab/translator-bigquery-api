from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid
import logging
import time
from datetime import datetime, timedelta
from app.api.bigquery.googleinterface import *


glogger = logging.getLogger()
KEY = settings.BIGQUERY_KEY
BUCKET = settings.BIGQUERY_BUCKET
PROJECT = settings.BIGQUERY_PROJECT

class QueryBuilder:
    """Generates and validates a provided query"""
    def __init__(self, table=settings.BIGQUERY_DEFAULT_TABLE,
            columns=[],
            genes_from=[],
            genes_to=[],
            restriction_gt=[],
            restriction_lt=[],
            restriction_bool=[],
            restriction_join='intersect',
            limit=10000,
            average_columns=False,
            error_messages=[]):
        self._project = settings.BIGQUERY_PROJECT
        self._dataset = settings.BIGQUERY_DATASET
        self._table = table
        self._columns = columns
        self._genes_from = genes_from
        self._genes_to = genes_to
        self._restriction_gt = restriction_gt
        self._restriction_lt = restriction_lt
        self._restriction_join = restriction_join
        self._restriction_bool = restriction_bool
        self._average_columns = average_columns
        self._limit = limit
        self._preparsing_errors = error_messages

    def invalid_table(self):
        ''' Validate table. If invalid, return the name of the table. '''
        if not self.get_table().exists():
            return ["Bad table: %s" % (self._table)]
        else:
            return []

    def invalid_columns(self):
        ''' Validate columns. Return invalid columns, if any. '''
        tbl_columns = self.get_column_names()
        missing_columns = ["Bad column: %s" % c for c in self._columns if c not in tbl_columns]
        return missing_columns

    def invalid_limit(self):
        ''' Validate row limit, checking if it is an integer and if integer is greater than 0. '''
        try:
            i = int(self._limit)
            if i >= 0:
                return []
            else:
                return ["Bad limit: [%s]" % (self._limit,)]
        except:
            return ["Bad limit: [%s]" % (self._limit,)]

    def invalid_genes(self):
        ''' Validate genes, checking if they are integers. '''
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
        ''' Validate restrictions by checking if the column is in the table and if the threshold value is a float '''
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
        for column, value in self._restriction_bool:
            if column not in tbl_columns:
                if value.strip() not in ['True', 'False']:
                    invalid_restriction.append("Bad value in restriction: %s = %s" % (column, value))
        if self._restriction_join.strip() not in ['intersect', 'union']:
            invalid_restriction.append("Invalid restriction join [%s].  Valid values are intersect or union.")

        return invalid_restriction

    def validate_query(self):
        ''' Validate each argument of the query to ensure approriate genes, tables,
                columns, strictions, and limits are requested

        Parameters
        ----------
        self

        Returns
        -------
        errors (list): list of errors, if any
        '''
        # First check if table is valid. If not, other checks would fail
        it = self.invalid_table()
        if len(it) > 0:
            errors = self._preparsing_errors + it
            return errors

        ic = self.invalid_columns()
        ig = self.invalid_genes()
        ir = self.invalid_restrictions()
        il = self.invalid_limit()

        errors = self._preparsing_errors + it + ic + ir + ig + il
        return errors

    def generate_query(self):
        sbase = ["GPID", "Gene1", "Gene2"]
        if len(self._columns):
            if not self._average_columns:
                SELECT = 'SELECT ' + ', '.join(sbase + self._columns)
            else:
                pickCol = self._columns
                Sum = '+'.join(['%s' % x for x in pickCol])
                N = '+'.join(["IF(%s IS NULL, 0, 1)" % x for x in pickCol])
                ave = "(%s)/(%s)" % (Sum, N)
                SELECT = 'SELECT ' + ', '.join(sbase)
                SELECT += ', %s as mean' % (ave,)
        else:
            SELECT = 'SELECT * '
        FROM = "FROM `%s.%s.%s`" % (self._project, self._dataset, self._table)
        WHERE = []
        for column, value in self._restriction_gt:
            line = " %s > %.5f " % (column, float(value))
            WHERE.append(line)
        for column, value in self._restriction_lt:
            line = " %s < %.5f " % (column,float(value) )
            WHERE.append(line)
        for column, value in self._restriction_bool:
            if value.strip() =='True':
                WHERE.append(column)
            else:
                WHERE.append('NOT %s' % (column,))
        gstring = ''
        if len(self._genes_to):
            gf = ','.join(self._genes_from)
            gt = ','.join(self._genes_to)
            gstring = "((Gene1 IN (%s) AND Gene2 IN (%s)) OR (Gene1 IN (%s) AND Gene2 IN (%s)))" % (gf, gt, gt, gf)
        elif len(self._genes_from):
            gf = ','.join(self._genes_from)
            gstring = "((Gene1 IN (%s) OR Gene2 IN (%s)))" % (gf, gf)
        if len(WHERE) and len(gstring):
            if self._restriction_join == 'intersect':
                WHERE = "WHERE " + gstring + ' AND ( %s )' % (' AND '.join(WHERE),)
            else:
                WHERE = "WHERE FDSFDS" + gstring + ' AND (%s )' % (' OR '.join(WHERE),)
        elif len(WHERE):
            if self._restriction_join == 'intersect':
                WHERE = "WHERE " + ' AND '.join(WHERE)
            else:
                WHERE = "WHERE "  + ' OR '.join(WHERE)
        elif len(gstring):
            WHERE = "WHERE " + gstring
        else:
            WHERE = ''

        LIMIT = "LIMIT %i" % (int(self._limit),)
        query = '\n'.join([SELECT, FROM, WHERE, LIMIT])

        glogger.debug("Query:\n%s" % (query,))
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

    def get_table_schema(self):
        tbl = self.get_table()
        if tbl.exists():
            tbl.reload()
            return [sc for sc in tbl.schema]
        else:
            glogger.exception("No such table [%s.%s]" % (self._project, self._table))
            raise Exception("No such table [%s.%s]" % (self._project, self._table))

    def list_tables(self):
        gi = GoogleInterface()
        # ignore metadata tables
        md = [settings.BIGQUERY_METADATA_COLUMNS,
                settings.BIGQUERY_METADATA_TISSUES]
        def is_temp(tname):
            return tname.find('_temp') > -1
        tables = []
        for table in gi.bq_client.dataset(self._dataset).list_tables():
            if table.name not in md and not is_temp(table.name):
                tables.append(table)
        return tables

    @classmethod
    def from_request(cls, request):
        """Generates QueryGenerator object from request

        Parameters
        ----------
        request (dict): Arguments to for query.
                        Includes restrictions on genes, columns, table, coefficients, p-values, rows, etc.

        Returns
        -------
        None

        """
        def parse_list(gstr):
            """ Parse a string representation of a list of genes

            Parameters
            ----------
            gstr (str): string representation of a list with no end brackets separated by commas.

            Returns
            -------
            list of string
            """
            return map(lambda x: x.strip(), gstr.split(','))

        def parse_restrictions(rstr):
            """ Parse a list of restrictions.
                Restrictions must be presented in pairs of (restriction_type, threshold_value)

            Parameters
            ----------
            rstr (str): string representation of list of restriction pairs

            Returns
            -------
            list of tuples where each tuple is a pair of restriction type and threshold

            """
            rlist = parse_list(rstr)
            restrictions = []

            # check to make sure length of restrictions are pairs of (restriction_type, threshold)
            if len(rlist) < 2 or len(rlist) % 2 != 0:
                raise Exception("Bad restriction")

            for i in range(len(rlist)/2):
                restrictions.append((rlist[2*i], rlist[2*i+1]))
            return restrictions

        error_messages = []
        rj = request
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
        if 'restriction_bool' in rj:
            try:
                args['restriction_bool'] = parse_restrictions(rj['restriction_bool'])
            except:
                error_messages += ['Unparseable restriction_bool [%s]' % (rj['restriction_bool'],)]
        if 'restriction_join' in rj:
            args['restriction_join'] = rj['restriction_join']
        if 'limit' in rj:
            args['limit'] = rj['limit']
        if 'average_columns' in rj:
            if rj['average_columns'] in ['false', 'False', 'FALSE','F', 0]:
                args['average_columns'] = False
            elif rj['average_columns'] in ['true', 'True', 'TRUE','T', 1]:
                args['average_columns'] = True
            else:
                error_messages += ['Unparseable average_columns [%s]' % (rj['average_columns'],)]
        if len(error_messages) > 0:
            args['error_messages'] = error_messages
        glogger.debug("Args object.[%s]" % (str(args),))
        return cls(**args)
