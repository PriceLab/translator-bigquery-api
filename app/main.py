import logging.config
logging.config.fileConfig('logging.conf')

import sys
sys.path.append('/')

from flask import Flask, Blueprint
from app import settings
from app.api.bigquery.endpoints.biggim import ns as biggim
from app.api.bigquery.endpoints.bigclam import ns as bigclam
from app.api.bigquery.endpoints.bglite import ns as bglite 
from app.api.bigquery.endpoints.interactions import ns as interactions
from app.api.bigquery.endpoints.metadata import ns as metadata
from app.api.restplus import api
from app.database import db

# this structure was ripped off from
# http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/


app = Flask("TranslatorAPI")
# Log initialization must happen after Flask initialization to print to stdout
applogger = logging.getLogger("app")
app.logger.addHandler(applogger)

def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    app.logger.info("Server is expecting hostname to be: {}".format(settings.FLASK_SERVER_NAME))
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['BIGQUERY_KEY'] = settings.BIGQUERY_KEY
    flask_app.config['BIGQUERY_BUCKET'] = settings.BIGQUERY_BUCKET


def initialize_app(app):
    app.logger.info("Starting Initialization")
    configure_app(app)
    app.logger.info("Configuration Finished")
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    app.logger.info("Blueprint loaded")
    api.init_app(blueprint)
    api.add_namespace(biggim)
    api.add_namespace(bglite)
    api.add_namespace(bigclam)
    api.add_namespace(interactions)
    api.add_namespace(metadata)
    app.logger.info("Finished adding namespaces")
    app.register_blueprint(blueprint)
    app.logger.info("Finished registering blueprint")
    db.init_app(app)
    app.logger.info("Finished initialize")

initialize_app(app)

@app.route("/")
def hello():
    app.logger.info("returning BigGIM API Link")
    return """<a href="http://biggim.ncats.io/api/">http://biggim.ncats.io/api/</a>"""


if __name__ == '__main__':
    app.logger.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0', debug=True, port=8080)
