from datetime import datetime
from app.database import db

class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Dataset(db.Model):
    __tablename__ = "dataset"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(80))

class Table(db.Model):
    __tablename__ = "table"
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.String(1000))
    num_rows = db.Column(db.Integer)
    num_bytes = db.Column(db.Integer)
    default = db.Column(db.Boolean)
    columns = db.relationship("Column", backref='table')

class Study(db.Model):
    __tablename__ = "study"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(1000))
    substudies = db.relationship("Substudy", backref='study')

class Substudy(db.Model):
    __tablename__ = "substudy"
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey('study.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.String(1000))
    cell_of_origin = db.Column(db.String(100))
    tissue_hierarchy = db.Column(db.String(100))
    columns = db.relationship("Column", backref='substudy')
    tissues = db.relationship("SubstudyTissue", backref='substudy')

class SubstudyTissue(db.Model):
    __tablename__ = "substudytissue"
    substudy_id = db.Column(db.Integer, db.ForeignKey('substudy.id'), primary_key=True)
    tissue = db.Column(db.String(100), primary_key=True)


class Column(db.Model):
    __tablename__ = "columns"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    interactions_type = db.Column(db.String(80))
    datatype = db.Column(db.String(80))
    substudy_id = db.Column(db.Integer, db.ForeignKey('substudy.id'))



