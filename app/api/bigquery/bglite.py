from app.api.bigquery.querytools import QueryBuilder
from app.database.models import SubstudyTissue, Substudy
from app import settings
import logging

glogger = logging.getLogger()

class BGLiteQueryBuilder(QueryBuilder):
    def __init__(self, table=settings.BIGQUERY_DEFAULT_TABLE,
            genes=[], tissue = 'whole_body', minR = 0.3, limit=10000,
            error_messages=[]):
        self._project = settings.BIGQUERY_PROJECT
        self._dataset = settings.BIGQUERY_DATASET
        self._table = table
        self._minR = minR
        self._genes = genes
        self._tissue = tissue
        self._limit = limit
        self._columns = None
        self._preparsing_errors = error_messages

    def validate_query(self):
        it = self.invalid_table()
        ir = self.invalid_restrictions()
        il = self.invalid_limit()
        ii = self.invalid_tissue()
        ig = self.invalid_genes()
        errors = self._preparsing_errors + it + ir + ig + il + ii
        return errors 

    def invalid_genes(self):
        bad_genes = []
        for g in self._genes:
            try:
                i = int(g)
            except:
                bad_genes.append(g)
        if len(self._genes) == 0:
            return ["ids is a required parameter"]
        if len(bad_genes):
            return ["Bad gene: %s" % (g) for g in bad_genes]
        else:
            return []

    def invalid_tissue(self):
        self._columns = self.get_columns()
        if len(self._columns) == 0:
            glogger.debug("bad tissue %s" % (self._tissue))
            return ["%s is not a valid a tissue." % (self._tissue,)]
        else:
            return []

    def invalid_restrictions(self):
        try:
            float(self._minR)
        except ValueError:
            return ["%s is not a valid minimum r." % (self._minR)]
        return []

    def get_columns(self):
        spear = "Spearman Rank Correlation Coefficient"
        st = SubstudyTissue.query.filter_by(tissue=self._tissue).all()
        columns = []
        if st:
            for s in st:
                glogger.debug("ssid %s" % (s.substudy_id))
                ss = Substudy.query.get(s.substudy_id)
                for c in ss.columns:
                    if c.table.name == self._table and c.interactions_type in [spear]:
                        columns.append(c.name)
        else:
            glogger.debug("No tissue found")
        glogger.debug("%s selected columns" % (columns))
        return columns

    def generate_query(self ):
        pickCol = self._columns
        geneList = self._genes
        minR = self._minR
        maxN = self._limit

        #column list
        clist = ', '.join(pickCol)
        #gene selection
        gtmp = "Gene1=%s OR Gene2=%s"
        gsel = ' OR '.join([gtmp % (g,g) for g in geneList])
        #r value selection
        ftmp = '(%s IS NOT null AND (%s > %f OR %s < %f))'
        rsel = ' AND '.join([ftmp % (f,f,float(minR), f, -1*float(minR) )for f in pickCol])
        # table name
        ptable = "%s.%s.%s" % (self._project, self._dataset, self._table)


        absSum = '+'.join(["ABS(%s)" % x for x in pickCol])
        ## we start with interm table t1 where we extract the genes and
        ## tissues of interest, while also thresholding on the correlation
        ## value
        t1 = """
        SELECT GPID, Gene1, Gene2, GREATEST(%s) AS maxCorr, 
            LEAST(%s) AS minCorr, (%s) as sumCorr, %s
        FROM `%s` 
        WHERE (%s) AND (%s)
        """ % (clist, clist, absSum, clist, ptable, gsel, rsel)

        j1 = """
        SELECT Gene1, b.Approved_Symbol AS Symbol1, Gene2, maxCorr, minCorr, sumCorr, %s
        FROM t1 a JOIN `isb-cgc.genome_reference.genenames_mapping` b 
            ON a.Gene1=CAST(b.Entrez_Gene_ID AS INT64)""" % (clist,)

        j2 = """
        SELECT Gene1, Symbol1, Gene2, b.Approved_Symbol AS Symbol2, maxCorr, minCorr, sumCorr, %s
        FROM j1 a JOIN `isb-cgc.genome_reference.genenames_mapping` b 
            ON a.Gene2=CAST(b.Entrez_Gene_ID AS INT64)  
        """ % (clist,)

        q  = """
        WITH 
        t1 AS (%s),
        j1 AS (%s),
        j2 AS (%s)
        SELECT Gene1, Symbol1, Gene2, Symbol2, maxCorr, minCorr, sumCorr, %s
        FROM j2 
        ORDER BY ABS(sumCorr) DESC
        LIMIT %d
        """ % (t1, j1, j2, clist, int(maxN))
        glogger.debug("Query [%s]" % (q,))
        return ( q )


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
        rj = request
        args = {}
        if 'ids' in rj:
            args['genes'] = parse_list(rj['ids'])
        if 'tissue' in rj:
            args['tissue'] =  rj['tissue']
        if 'minR' in rj:
            args['minR'] = rj['minR']
        if 'table' in rj:
            args['table'] = rj['table']
        if 'limit' in rj:
            args['limit'] = rj['limit']
        if len(error_messages) > 0:
            args['error_messages'] = error_messages
        glogger.debug("Args object.[%s]" % (str(args),))
        return cls(**args)
