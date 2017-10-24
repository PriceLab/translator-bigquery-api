# Flask settings

FLASK_SERVER_NAME = 'biggim.ncats.io'
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

#Bigquery settings

BIGQUERY_KEY = '/cred/miRNA project-01ca75e6de66.json'
BIGQUERY_DATABASE_PASSWORD = '/cred/database_reset.json'
BIGQUERY_BUCKET = 'ncats_bigquery_results'
BIGQUERY_PROJECT = 'isb-cgc-04-0010'
BIGQUERY_DATASET = 'NTTB_BigGIM'
BIGQUERY_DEFAULT_TABLE = 'BigGIM_70_v1'
BIGQUERY_METADATA_DIRECTORY = '/cred/metadata'
BIGQUERY_METADATA_COLUMNS = 'metadata_columns'
BIGQUERY_METADATA_TISSUES = 'metadata_tissues'
