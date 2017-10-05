import logging
import traceback

from flask_restplus import Api
from app import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

log.debug("In restplus")
api = Api(version='1.0', title='Blue Team Bigquery Demo',
          description='API for accessing bigquery similarity scores')


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

