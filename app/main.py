import logging.config
import sys
sys.path.append('/')



from flask import Flask, Blueprint
from app import settings
from app.api.bigquery.endpoints.interactions import ns as interactions
from app.api.bigquery.endpoints.metadata import ns as metadata
from app.api.bigquery.endpoints.bigclam import ns as bigclam
from app.api.restplus import api
from app.database import db

# this structure was ripped off from
# http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/


app = Flask(__name__)
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['BIGQUERY_KEY'] = settings.BIGQUERY_KEY
    flask_app.config['BIGQUERY_BUCKET'] = settings.BIGQUERY_BUCKET


def initialize_app(app):
    log.info("Test log")
    configure_app(app)
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(interactions)
    api.add_namespace(metadata)
    api.add_namespace(bigclam)
    app.register_blueprint(blueprint)
    db.init_app(app)
    log.info("finished initialize")

initialize_app(app)

@app.route("/")
def hello():
    return """<a href="http://biggim.ncats.io/api/">http://biggim.ncats.io/api/</a>"""

if __name__ == '__main__':
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0', debug=True, port=80)
