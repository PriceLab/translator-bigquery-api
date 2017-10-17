import logging
from app import settings
from app.database import db, reset_database
from app.api.bigquery.querytools import QueryBuilder
import os.path
import pandas

log = logging.getLogger(__name__)


def populate_database():
    from app.database.models import Project, Dataset, Table, Study, Substudy, \
            SubstudyTissue, Column
    reset_database()
    log.debug("Adding project")
    project = Project(name=settings.BIGQUERY_PROJECT)
    db.session.add(project)
    db.session.commit()
    log.debug("Adding dataset")
    dataset = Dataset(name=settings.BIGQUERY_DATASET, project_id=project.id)
    db.session.add(dataset)
    db.session.commit()

    qb = QueryBuilder(table=None)
    tmeta = []
    substudies = set()
    studies = set()
    for t in qb.list_tables():
        t.reload()
        log.debug("Adding table [%s]" % (t.name))
        dt = Table(name=t.name, description=t.description, 
                   dataset_id=dataset.id, num_rows=t.num_rows, 
                   num_bytes=t.num_bytes, 
                   default=True if t.name == settings.BIGQUERY_DEFAULT_TABLE else False)
        db.session.add(dt)
        db.session.commit()
        md_file = os.path.join(settings.BIGQUERY_METADATA_DIRECTORY,
                               "%s.tsv" % (t.name,))
        # a metadata file is present, annotate metadata

        if os.path.exists(md_file):
            log.debug("Adding columns for %s" % (t.name))
            ca = pandas.read_csv(md_file, delimiter='\t')
            ca = ca.set_index('Column_ID')
            qb2 = QueryBuilder(table=t.name)
            columns = qb2.get_table_schema()
            tissues = ca.columns.tolist()[8:]
            for column in columns:
                if column.name in ['GPID','Gene1','Gene2']:
                    #don't document these columns
                    pass     
                else:
                    log.debug("Adding column [%s.%s]" % (dt.name, column.name) )
                    column_id = '_'.join(column.name.split('_')[:-1])
                    interactions_type = column.name.split('_')[-1]
                    cmd = ca.loc[column_id]
                    if cmd['Study'] not in studies:
                        log.debug("Creating study [%s]" % (cmd['Study'],))
                        study = Study( name=cmd['Study'],
                                description=cmd['Study'])
                        db.session.add(study)
                        db.session.commit()
                        studies.add(cmd['Study'])
                    else:
                        study = db.session.query(Study).filter(
                                Study.name ==cmd['Study']).first()
                    if cmd['Study ID'] not in substudies:
                        log.debug("Creating substudy [%s]" % (cmd['Study Name'],))
                        substudy=Substudy(name=cmd['Study ID'], 
                                description=cmd['Study Name'],
                                cell_of_origin=cmd['Cell of Origin'],
                                tissue_hierarchy=cmd['Tissue Hierarchy'],
                                study_id=study.id)
                        db.session.add(substudy)
                        db.session.commit()
                        for t in cmd[tissues].dropna().index.tolist():
                            log.debug("Adding [%i-%s]" % (substudy.id, t))
                            tissue=SubstudyTissue(substudy_id=substudy.id,
                                    tissue=t)
                            db.session.add(tissue)
                        db.session.commit()
                        substudies.add(cmd['Study ID'])
                    else:
                        substudy = db.session.query(Substudy).filter(
                                Substudy.name ==cmd['Study ID']).first()
                    log.debug("ssid %i" % substudy.id)
                    c = Column(name=column.name, 
                            table_id=dt.id, 
                            interactions_type=interactions_type,
                            datatype=column.field_type,
                            substudy_id=substudy.id
                            )
                    db.session.add(c)
                    db.session.commit()
        elif False:
            pass
            log.debug("Adding columns for %s" % (t.name))
            qb2 = QueryBuilder(table=t.name)
            columns = qb2.get_table_schema()
            for column in columns:
                if column.name in ['GPID','Gene1','Gene2']:
                    pass     
                else:
                    log.debug("Adding column [%s.%s]" % (dt.name, column.name) )
                    column_id = '_'.join(column.name.split('_')[:-1])
                    interactions_type = column.name.split('_')[-1]
                    c = Column(name=column.name, 
                            table_id=dt.id, 
                            interactions_type=interactions_type,
                            datatype=column.field_type
                            )
                    db.session.add(c)
    db.session.commit()

