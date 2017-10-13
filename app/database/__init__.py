from flask_sqlalchemy import SQLAlchemy
from app import settings
import logging

log = logging.getLogger(__name__)
db = SQLAlchemy()


def reset_database():
    from app.database.models import Project
    db.drop_all()
    db.create_all()
