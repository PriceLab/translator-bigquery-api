from app.database import db
from app import settings
from app.api.bigquery.querytools import *
from app.database.models import *
from flask_restplus import marshal
from app.api.bigquery.serializers import table_response, column_response, substudy_response, study_response

import uuid, logging
import math

glogger = logging.getLogger()


def get_table(table_name=None):
    """Returns table with given table name.
    """
    project_id = Project.query.filter_by(name=settings.BIGQUERY_PROJECT).first().id
    dataset_id = Dataset.query.filter_by(name=settings.BIGQUERY_DATASET).first().id
    if table_name is not None:
        table = Table.query.filter_by(name=table_name, 
                dataset_id=dataset_id).first()
        columns = get_columns(table)
        table_dict = marshal(table, table_response)
        table_dict['columns'] = columns
        return table_dict
    else:
        # all tables
        return Table.query.filter_by(dataset_id=dataset_id).all()


def get_column(table_name, column_name):
    project_id = Project.query.filter_by(name=settings.BIGQUERY_PROJECT).first().id
    dataset_id = Dataset.query.filter_by(name=settings.BIGQUERY_DATASET).first().id
    table = Table.query.filter_by(name=table_name, 
                dataset_id=dataset_id).first()
    column = Column.query.filter_by(name=column_name,
                                    table_id=table.id).first()
    cdict = marshal(column, column_response)
    substudy = Substudy.query.get(column.substudy_id)
    ssdict = marshal(substudy, substudy_response)
    study = Study.query.get(substudy.study_id)
    ssdict['study'] = marshal(study, study_response)
    cdict['substudy'] = ssdict
    return cdict

def get_columns(table):
    result = []
    columns = Column.query.filter_by(table_id=table.id).all()
    for column in columns:
        cdict = marshal(column, column_response)
        substudy = Substudy.query.get(column.substudy_id)
        ssdict = marshal(substudy, substudy_response)
        study = Study.query.get(substudy.study_id)
        ssdict['study'] = marshal(study, study_response)
        cdict['substudy'] = ssdict
        result.append(cdict)
    return result
