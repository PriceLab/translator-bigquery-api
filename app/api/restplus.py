import logging
import traceback

from flask_restplus import Api
from app import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

log.debug("In restplus")
api = Api(version='1.0', title='Big GIM(Gene Interaction Miner)',
        description="""Big GIM (Gene Interaction Miner) is a Translator Knowledge Source that contains function interaction data for all pairs of genes. Functional interaction data are available from four different sources: 1) tissue-specific gene expression correlations from healthy tissue samples (GTEx), 2) tissue-specific gene expression correlations from cancer samples (TCGA), 3) tissue-specific probabilities of function interaction (GIANT), and 4) direct interactions (BioGRID). The data is stored as a Google BigQuery table enabling fast access.""")


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
