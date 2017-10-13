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
    log.debug("Adding dataset")
    dataset = Dataset(name=settings.BIGQUERY_DATASET, project_id=project.id)
    db.session.add(dataset)

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
                   disabled=True)
        db.session.add(dt)
        md_file = os.path.join(settings.BIGQUERY_METADATA_DIRECTORY,
                               "%s.tsv" % (t.name,))
        # a metadata file is present, so annotate metadata

        if os.path.exists(md_file):
            log.debug("Adding columns for %s" % (t.name))
            dt.disabled = False 
            ca = pandas.read_csv(md_file, delimiter='\t')
            ca = ca.set_index('Column_ID')
            qb2 = QueryBuilder(table=t.name)
            columns = qb2.get_column_names()
            for column in columns:
                if column in ['GPID','Gene1','Gene2']:
                    pass     
                else:

                    column_id = '_'.join(column.split('_')[:-1])
                    similarity_type = column.split('_')[-1]
                    c = Column(name=column, 
                            table_id=dt.id, 
                            similarity_type=similarity_type)
                    cmd = ca.loc[column_id]
                    if cmd['Study'] not in studies:
                        study = Study(abbr=cmd['Study'], name=cmd['Study'],
                                description=cmd['Study'])
                        db.session.add(study)
                        studies.add(cmd['Study'])
                    else:
                        study = db.session.query(Study).filter(
                                Study.name ==cmd['Study']).first()

                    if cmd['Study ID'] not in substudies:
                        substudy=Substudy(name=cmd['Study ID'], 
                                description=cmd['Study Name'],
                                cell_of_origin=cmd['Cell Of Origin'],
                                tissue_heirarchy=cmd['Tissue Heirarchy'],
                                study_id=study.id)
                        db.session.add(substudy)
                        studies.add(cmd['Study ID'])
                    else:
                        substudy = db.session.query(Substudy).filter(
                                Substudy.name ==cmd['Study ID']).first()
                    c.substudy_id = substudy.id
                    db.session.add(c)
    db.session.commit()

