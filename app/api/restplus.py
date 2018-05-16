import logging
import traceback

from flask_restplus import Api
from app import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

log.debug("In restplus")
api = Api(version='2.0', title='Big GIM and Big CLAM',
        description="""**Big GIM** (Gene Interaction Miner) is an **NCATS Translator Knowledge Source** that contains function interaction data for all pairs of genes. Functional interaction data are available from four different sources: 1) tissue-specific gene expression correlations from healthy tissue samples (GTEx), 2) tissue-specific gene expression correlations from cancer samples (TCGA), 3) tissue-specific probabilities of function interaction (GIANT), and 4) direct interactions (BioGRID). These data are stored as a Google BigQuery tables enabling fast access and real-time association analysis.
        
**Big CLAM** (Cell Line Association Miner) is an **NCATS Translator Knowledge Source** that integrates large-scale high-quality data of various cell line resources to uncover associations between genomic and molecular features of cell lines, drug response measurements and gene knockdown viability scores. The cell line data comes from five different sources: 1) CCLE - Cancer Cell Line Encyclopedia, 2) GDSC - Genomics of Drug Sensitivity in Cancer, 3) CTRP - Cancer Therapeutics Response Portal, 4) CMap - Connectivity Map, and 5) CDM - Cancer Dependency Map. These data are stored as a Google BigQuery tables enabling fast access and real-time association analysis.
        """)


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404
