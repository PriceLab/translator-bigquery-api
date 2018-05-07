from app.database import db
from app import settings

from google.cloud import bigquery
from google.cloud import storage
import uuid, logging
import time
import numpy as np
from datetime import datetime, timedelta


glogger = logging.getLogger()


class BCQueryBuilder:
    def __init__(self, genes=[], query_type=None):
        self._genes = genes
        self._preparsing_errors = []
        self._query_type = query_type

    def validate_query(self):
        ig = self.invalid_genes()
        errors = self._preparsing_errors + ig
        return errors

    def invalid_genes(self):
        bad_genes = []
        #TODO: check genes
        if len(bad_genes):
            return ["Bad gene: %s" % (g) for g in bad_genes]
        else:
            return []

    def invalid_query_type(self):
        if self._query_type not in ['g2g','g2d']:
            return ["Bad query type: %s" % (self._query_type)]
        else:
            return []

    @classmethod
    def from_request(cls, request, query_type):
        def parse_list(gstr):
            return map(lambda x: x.strip(), gstr.split(','))
        error_messages = []
        rj = request
        args = {}
        if 'ids' in rj:
            args['genes'] = parse_list(rj['ids'])
        args['query_type'] = query_type

        glogger.debug("Args object.[%s]" % (str(args),))
        return cls(**args)

    @property
    def genes(self):
        return self._genes

    def generate_query(self):
        glogger.warning(self.base_query)
        glogger.warning(self.genes_subquery)
        return self.base_query % self.genes_subquery

    @property
    def genes_subquery(self):
        return ' UNION ALL '.join(["SELECT '%s'" % (g,) for g in self.genes])

    @property
    def base_query(self):
        if self._query_type == 'g2d':
            return self.gene2drug()
        elif self._query_type=='g2g':
            return self.gene2gene()
        else:
            raise Exception("[%s] is unknown query type")

    def gene2gene(self):
        return """
WITH
  --
  -- we query the Copy_Number data in two steps:
  -- first:  we select the cell-lines and genes in our gene-list and
  -- calculate the difference in CN across the gene;
  -- second: we keep only those cell-lines and genes where the "delta CN"
  -- exceeds a certain threshold
  --
  -- in this particular hard-coded example, interim result CN_t1 contains
  -- 9960 rows, with 996 cell-lines x 10 genes (our gene-list has 10 genes),
  -- and the range of "delta CN" values is between 0 and 12
  -- (with 0 occurring 99 of the time)
  --
  -- interim result CN_t2 contains just 11 rows: 11 distinct cell-lines,
  -- each of which has significant CN variation across one of our genes of interest
  --
  SOURCE_GENES AS (%s),
  CN_t1 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol,
    (max_CN-min_CN) AS del_CN
  FROM
    `isb-cgc-04-0002.GDSC_v0.Copy_Number_Variation`
  WHERE
    HGNC_gene_symbol IN (
    SELECT
      *
    FROM
      SOURCE_GENES)
  GROUP BY
    1,
    2,
    3 ),
  CN_t2 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol
  FROM
    CN_t1
  WHERE
    del_CN >= 4 ),
  --
  -- next we query the variants table
  -- (we're missing the effects of gene fusions right now, but that can be fixed)
  --
  -- in this particular hard-coded example, we will get back an
  -- interim table with 877 rows: 575 cell-lines with variants in our list
  -- of 10 genes; ~90 of cell-lines have variants in one or two genes
  -- but 4 cell-lines have variants in 7 of our (well-chosen!) genes
  --
  V_t1 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol
  FROM
    `isb-cgc-04-0002.GDSC_v0.WES_variants`
  WHERE
    HGNC_gene_symbol IN (
    SELECT
      *
    FROM
      SOURCE_GENES  )
  GROUP BY
    1,
    2),
  --
  -- now we are going to create a union of our two lists of
  -- cell-lines and genes from the copy-number and variant
  -- queries above
  --
  -- in this particular example, the list is dominated by the
  -- variants-based result with 877 rows, with only 11 additional
  -- rows provided by the CN result; 582 cell-lines and all 10
  -- of our (well-chosen) genes are represented
  --
  U1 AS (
  SELECT
    *
  FROM
    CN_t2
  UNION ALL
  SELECT
    *
  FROM
    V_t1 ),
  --
  -- from the above able, we create our first "metric" for each
  -- cell-line which is simply a count of how many genes (in our list)
  -- are "altered" in each cell-line
  --
  M1 AS (
  SELECT
    Cell_Line_Name,
    COUNT(*) AS metric1
  FROM
    U1
  GROUP BY
    1 ),
  --
  -- we need to add in rows with metric1=0 for all cell-lines that
  -- did *not* have an "alteration" in one of our genes
  --
  M2 AS (
  SELECT
    Cell_Line_Name,
    0 AS temp
  FROM
    `isb-cgc-04-0002.GDSC_v0.WES_variants`
  GROUP BY
    1,
    2 ),
  M3 AS (
  SELECT
    a.Cell_Line_Name,
    a.temp + IFNULL(b.metric1,
      0) AS metric1
  FROM
    M2 a
  LEFT JOIN
    M1 b
  ON
    a.Cell_Line_Name=b.Cell_Line_Name ),
  --
  -- and then we turn this metric into a rank; since this metric is
  -- a simple count, the ranking process will likely simply reverse
  -- the order where a "high" metric will result in a "low" rank
  -- (a rank of "1" being "best")
  --
  R1 AS (
  SELECT
    Cell_Line_Name,
    metric1,
    DENSE_RANK() OVER (ORDER BY metric1 DESC) AS rank1
  FROM
    M3 ),
  --
  -- here we will bring in the CDM data
  -- which we do by joining the result that we have so far with
  -- the gene_knockdown_CellLineAnnotation table, and calling the gene_knockdownZ our second metric
  --
  -- this step dramatically increases the size of our current/working
  -- result since the gene knockdown table contains information for
  -- all genes on each cell-line
  --
  J1 AS (
  SELECT
    a.Cell_Line_Name,
    a.metric1,
    a.rank1,
    b.gene_symbol,
    b.gene_knockdownZ AS metric2
  FROM
    R1 a
  JOIN
    `isb-cgc-04-0002.CDM_v0.gene_knockdown_CellLineAnnotation` b
  ON
    a.Cell_Line_Name=b.cell_line_id ),
  --
  -- now that we have our drug-response based metric, we will turn that
  -- into a ranking as well: this time a rank of 1 will be assigned to the
  -- drug with lowest IC50 value in that particular cell-line
  --
  R2 AS (
  SELECT
    Cell_Line_Name,
    metric1,
    rank1,
    gene_symbol,
    metric2,
    DENSE_RANK() OVER (PARTITION BY Cell_Line_Name ORDER BY metric2 ASC) AS rank2
  FROM
    J1 ),
  C1 AS (
  SELECT
    gene_symbol,
    CORR(metric1,
      metric2) AS corr1,
    CORR(rank1,
      rank2) AS corr2
  FROM
    R2
  GROUP BY
    gene_symbol ),
  J2 AS (
  SELECT
    DENSE_RANK() OVER (ORDER BY corr2 DESC) AS Gene_Rank,
    a.gene_symbol,
    a.corr1,
    a.corr2
  FROM
    C1 a),
  F1 AS (
  SELECT
    Gene_Rank,
    gene_symbol,
    corr2 AS Gene_Score
  FROM
    J2
  WHERE
    Gene_rank <= 10 )
SELECT
  *
FROM
  F1
ORDER BY
  Gene_Rank ASC
  """


    def gene2drug(self):
        return """
WITH
  --
  -- we query the Copy_Number data in two steps:
  -- first:  we select the cell-lines and genes in our gene-list and
  -- calculate the difference in CN across the gene;
  -- second: we keep only those cell-lines and genes where the "delta CN"
  -- exceeds a certain threshold
  --
  -- in this particular hard-coded example, interim result CN_t1 contains
  -- 9960 rows, with 996 cell-lines x 10 genes (our gene-list has 10 genes),
  -- and the range of "delta CN" values is between 0 and 12
  -- (with 0 occurring 99 of the time)
  --
  -- interim result CN_t2 contains just 11 rows: 11 distinct cell-lines,
  -- each of which has significant CN variation across one of our genes of interest
  --
  SOURCE_GENES AS (%s),
  CN_t1 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol,
    (max_CN-min_CN) AS del_CN
  FROM
    `isb-cgc-04-0002.GDSC_v0.Copy_Number_Variation`
  WHERE
    HGNC_gene_symbol IN (
    SELECT
      *
    FROM
      SOURCE_GENES   )
  GROUP BY
    1,
    2,
    3 ),
  CN_t2 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol
  FROM
    CN_t1
  WHERE
    del_CN >= 4 ),
  --
  -- next we query the variants table
  -- (we're missing the effects of gene fusions right now, but that can be fixed)
  --
  -- in this particular hard-coded example, we will get back an
  -- interim table with 877 rows: 575 cell-lines with variants in our list
  -- of 10 genes; ~90 of cell-lines have variants in one or two genes
  -- but 4 cell-lines have variants in 7 of our (well-chosen!) genes
  --
  V_t1 AS (
  SELECT
    Cell_Line_Name,
    HGNC_gene_symbol
  FROM
    `isb-cgc-04-0002.GDSC_v0.WES_variants`
  WHERE
    HGNC_gene_symbol IN (
    SELECT
      *
    FROM
      SOURCE_GENES )
  GROUP BY
    1,
    2),
  --
  -- now we are going to create a union of our two lists of
  -- cell-lines and genes from the copy-number and variant
  -- queries above
  --
  -- in this particular example, the list is dominated by the
  -- variants-based result with 877 rows, with only 11 additional
  -- rows provided by the CN result; 582 cell-lines and all 10
  -- of our (well-chosen) genes are represented
  --
  U1 AS (
  SELECT
    *
  FROM
    CN_t2
  UNION ALL
  SELECT
    *
  FROM
    V_t1 ),
  --
  -- from the above able, we create our first "metric" for each
  -- cell-line which is simply a count of how many genes (in our list)
  -- are "altered" in each cell-line
  --
  M1 AS (
  SELECT
    Cell_Line_Name,
    COUNT(*) AS metric1
  FROM
    U1
  GROUP BY
    1 ),
  --
  -- we need to add in rows with metric1=0 for all cell-lines that
  -- did *not* have an "alteration" in one of our genes
  --
  M2 AS (
  SELECT
    Cell_Line_Name,
    0 AS temp
  FROM
    `isb-cgc-04-0002.GDSC_v0.WES_variants`
  GROUP BY
    1,
    2 ),
  M3 AS (
  SELECT
    a.Cell_Line_Name,
    a.temp + IFNULL(b.metric1,
      0) AS metric1
  FROM
    M2 a
  LEFT JOIN
    M1 b
  ON
    a.Cell_Line_Name=b.Cell_Line_Name ),
  --
  -- and then we turn this metric into a rank; since this metric is
  -- a simple count, the ranking process will likely simply reverse
  -- the order where a "high" metric will result in a "low" rank
  -- (a rank of "1" being "best")
  --
  R1 AS (
  SELECT
    Cell_Line_Name,
    metric1,
    DENSE_RANK() OVER (ORDER BY metric1 DESC) AS rank1
  FROM
    M3 ),
  --
  -- now we are ready to start bringing in drug response information,
  -- which we do by joining the result that we have so far with
  -- the Drug_Response table, and calling the IC50 our second metric
  --
  -- this step dramatically increases the size of our current/working
  -- result since the Drug_Response table contains information for
  -- up to 265 different drugs tested on each cell-line
  --
  J1 AS (
  SELECT
    a.Cell_Line_Name,
    a.metric1,
    a.rank1,
    b.Drug_identifier,
    b.IC50 AS metric2
  FROM
    R1 a
  JOIN
    `isb-cgc-04-0002.GDSC_v0.Drug_Response` b
  ON
    a.Cell_Line_Name=b.Cell_Line_Name ),
  --
  -- now that we have our drug-response based metric, we will turn that
  -- into a ranking as well: this time a rank of 1 will be assigned to the
  -- drug with lowest IC50 value in that particular cell-line
  --
  R2 AS (
  SELECT
    Cell_Line_Name,
    metric1,
    rank1,
    Drug_identifier,
    metric2,
    DENSE_RANK() OVER (PARTITION BY Cell_Line_Name ORDER BY metric2 ASC) AS rank2
  FROM
    J1 ),
  C1 AS (
  SELECT
    Drug_identifier,
    CORR(metric1,
      metric2) AS corr1,
    CORR(rank1,
      rank2) AS corr2
  FROM
    R2
  GROUP BY
    Drug_identifier ),
  J2 AS (
  SELECT
    DENSE_RANK() OVER (ORDER BY corr2 DESC) AS Drug_Rank,
    a.Drug_identifier,
    a.corr1,
    a.corr2,
    b.Drug_Name,
    b.Drug_Action,
    b.Drug_Putative_Target AS Drug_Target1,
    b.Drug_Targeted_process_or_pathway AS Drug_Target2
  FROM
    C1 a
  JOIN
    `isb-cgc-04-0002.GDSC_v0.Drug_Details` b
  ON
    a.Drug_identifier=b.Drug_identifier ),
  F1 AS (
  SELECT
    Drug_Rank,
    corr2 AS Drug_Score,
    Drug_Name,
    Drug_Target1,
    Drug_Target2
  FROM
    J2
  WHERE
    Drug_rank <= 10 )
SELECT
  *
FROM
  F1
ORDER BY
  Drug_Rank ASC
  

"""

