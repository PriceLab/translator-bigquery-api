import sys
sys.path.append('../../')

from behave import *

import sqlalchemy
from sqlalchemy import orm
from app.database.factories import *
from app.main import app, db

@given('a configured sqlalchemy engine')
def step_configure_sqlalchemy(context):
    engine = sqlalchemy.create_engine('sqlite://')
    # It's a scoped_session, and now is the time to configure it.
    Session = orm.scoped_session(orm.sessionmaker())
    Session.configure(bind=engine)
    context.sqlalchemy_configured = True
    context.Session = Session
    context.session = Session()
    with app.app_context():
      # TODO: FIX why this isn't creating the tables in the database
      db.create_all()
      db.session.expire_on_commit = False

@then('reset sqlalchemy database')
def reset_sqlalchemy(context):
  session = context.session
  session.rollback()
  Session = context.Session
  Session.remove()