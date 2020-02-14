import logging
from app import settings
from app.database import db, reset_database
from app.api.bigquery.querytools import QueryBuilder, GoogleInterface
import os.path
import pandas
import uuid
from app.database.models import Project, Dataset, Table, Study, Substudy, \
            SubstudyTissue, Column

log = logging.getLogger(__name__)

import pandas

STUDY_DESCRIPTIONS = {
        'BioGRID':""" Biological General Repository for Interaction Datasets
        BioGRID is an interaction repository with data compiled through comprehensive curation efforts.

        https://thebiogrid.org/
        """,
        'TCGA': """ The Cancer Genome Atlas
        The Cancer Genome Atlas (TCGA) is a collaboration between the National Cancer Institute (NCI) and the National Human Genome Research Institute (NHGRI) that has generated comprehensive, multi-dimensional maps of the key genomic changes in 33 types of cancer. The TCGA dataset, comprising more than two petabytes of genomic data, has been made publically available, and this genomic information helps the cancer research community to improve the prevention, diagnosis, and treatment of cancer.

        https://cancergenome.nih.gov/
        """,
        'GIANT':"""Genetic Investigation of ANthropometric Traits
        The Genetic Investigation of ANthropometric Traits (GIANT) consortium is an international collaboration that seeks to identify genetic loci that modulate human body size and shape, including height and measures of obesity. The GIANT consortium is a collaboration between investigators from many different groups, institutions, countries, and studies, and the results represent their combined efforts. The primary approach has been meta-analysis of genome-wide association data and other large-scale genetic data sets. Anthropometric traits that have been studied by GIANT include body mass index (BMI), height, and traits related to waist circumference (such as waist-hip ratio adjusted for BMI, or WHRadjBMI). Thus far, the GIANT consortium has identified common genetic variants at hundreds of loci that are associated with anthropometric traits.

        http://portals.broadinstitute.org/collaboration/giant/index.php/GIANT_consortium
        """,
        'GTEx':"""Genotype-Tissue Expression (GTEx) program

        Genotype-Tissue Expression (GTEx) program is providing valuable insights into the mechanisms of gene regulation by studying human gene expression and regulation in multiple tissues from health individuals; exploring disease-related perturbations in a variety of human diseases; and examining sexual dimorphisms in gene expression and regulation in multiple tissues. Genetic variation between individuals underlying the many differences in gene expression  will be examined for correlation with differences in gene expression level to identify regions of the genome that influence whether and how much a gene is expressed. Identifying unique genomic variations associated with gene expression is expected to stimulate research towards understanding the genetic basis of complex diseases. 
        
        https://www.gtexportal.org/home/
        """
        }

def get_metadata_columns():
    query = """Select *
           FROM [%s:%s.%s]
           """ % (settings.BIGQUERY_PROJECT, settings.BIGQUERY_DATASET,
                   settings.BIGQUERY_METADATA_COLUMNS)
    gi = GoogleInterface()
    query_job = gi.bq_client.run_async_query(str(uuid.uuid4()), query)

    query_job.begin()
    query_job.result()  # Wait for job to complete.

    # Print the results.
    destination_table = query_job.destination
    destination_table.reload()
    #return destination_table
    columns = [x.name for x in destination_table.schema[:]]
    table = [row for row in destination_table.fetch_data()]
    return pandas.DataFrame(table, columns=columns)

def add_study(study_name, study_description):
    st = Study.query.filter_by(name=study_name).first()
    if st is None:
        st = Study(name=study_name, 
                   description=study_description)
        db.session.add(st)
        db.session.commit()
    return st


def add_substudy(study_id, name, description, cell_of_origin, tissue_hierarchy):
    sst = Substudy.query.filter_by(name=name).first()
    if sst is None:
        sst = Substudy(study_id=study_id, name=name, description=description,
                    cell_of_origin=cell_of_origin, 
                    tissue_hierarchy=tissue_hierarchy)
        db.session.add(sst)
        db.session.commit()
    return sst

def add_table(table, dataset):
    dt = Table.query.filter_by(name=table.name).first()
    if dt is None:
        dt = Table(name=table.name, description=table.description,
                   dataset_id=dataset.id, num_rows=table.num_rows,
                   num_bytes=table.num_bytes,
                   default=True if table.name == settings.BIGQUERY_DEFAULT_TABLE else False)
        db.session.add(dt)
        db.session.commit()
    return dt

def add_studies_substudies():
    tmeta = get_metadata_columns()
    for s in tmeta.Study.unique().tolist():
        log.debug("Creating Study: [%s]" % (s,))
        st = add_study(s,STUDY_DESCRIPTIONS[s])
        smeta = tmeta[tmeta.Study == s][['Study_ID', 'Study_Name', 
            'Cell_of_Origin', 'Tissue_Hierarchy']].drop_duplicates()
        if len(smeta):
            for i, row in smeta.iterrows():
                if row.Study_ID is not None:
                    log.debug("Creating Substudy [%s.%s]" % (s, row.Study_ID))
                    add_substudy(st.id, row.Study_ID, row.Study_Name, row.Cell_of_Origin, row.Tissue_Hierarchy)
                if row.Study_ID is None:
                    log.debug("Creating Substudy [%s.%s]" % (s,'Default' ))
                    add_substudy(st.id, 'Default', 'Default', 
                        None, None)

def get_metadata_tissues():
    query = """Select *
           FROM [%s:%s.%s]
           """ % (settings.BIGQUERY_PROJECT, settings.BIGQUERY_DATASET,
                   settings.BIGQUERY_METADATA_TISSUES)
    gi = GoogleInterface()
    query_job = gi.bq_client.run_async_query(str(uuid.uuid4()), query)

    query_job.begin()
    query_job.result()  # Wait for job to complete.

    # Print the results.
    destination_table = query_job.destination
    destination_table.reload()
    #return destination_table
    columns = [x.name for x in destination_table.schema[:]]
    table = [row for row in destination_table.fetch_data()]
    return pandas.DataFrame(table, columns=columns)

def add_columns(table):
    # a metadata file is present, annotate metadata
    log.debug("Adding columns for %s" % (table.name))
    tname = "%s:%s.%s" % (settings.BIGQUERY_PROJECT,
                              settings.BIGQUERY_DATASET, table.name)
    tmeta = get_metadata_columns()
    tmeta_columns = tmeta[tmeta.Table == tname].set_index('Column_ID', verify_integrity=True)
    qb2 = QueryBuilder(table=table.name)
    columns = qb2.get_table_schema()
    for column in columns:
        if column.name in ['GPID','Gene1','Gene2']:
            #don't document these columns
            pass
        else:
            log.debug("Adding column [%s.%s]" % (table.name, column.name) )
            cmd = tmeta_columns.loc[column.name]
            study_name = cmd.Study
            if cmd.Study_ID is not None:
                log.debug("looking for %s.%s" % (cmd.Study, cmd.Study_ID))
                st=Study.query.filter_by(name=cmd.Study).first()
                sst = Substudy.query.filter_by(name=cmd.Study_ID, 
                                               study_id=st.id).first()
                sst_id = sst.id

            else:
                # if no substudy in meta, we created a default one
                st=Study.query.filter_by(name=cmd.Study).first()
                sst = Substudy.query.filter_by(name='Default', 
                                               study_id=st.id).first()
                sst_id = sst.id
            c = Column(name=column.name,
                    table_id=table.id,
                    interactions_type=cmd['Data_Type'],
                    datatype=column.field_type,
                    substudy_id=sst_id
                    )
            db.session.add(c)
            db.session.commit()

def add_tissues():
    """This is ugly, I should reformat this table"""
    parsed = []
    tmeta = get_metadata_columns()
    tissues = get_metadata_tissues()
    log.debug("Parsing Tissues table")
    for i,t in tissues.iterrows():
        a = tmeta[(tmeta.Table == t.Table) &  (tmeta.Column_ID == t.Column_ID)][['Study', 'Study_ID']].iloc[0]
        t['Study'] = a.Study
        t['Study_ID'] =  a.Study_ID
        parsed.append(t)

    parse_table = pandas.concat(parsed, axis=1).transpose().drop(['Column_ID', 'Table'], axis=1).drop_duplicates()
    tissue_d = {}
    log.debug("Making tissue lists." )
    for i, r in parse_table.set_index(['Study', 'Study_ID']).iterrows():
        my_tissues = r.dropna().index.tolist()
        if len(my_tissues):
            tissue_d[i] = my_tissues
        else:
            tissue_d[('BioGRID', 'Default')] = [u'whole_body']
    for k, v in tissue_d.iteritems():
        study_name, substudy_name = k
        st=Study.query.filter_by(name=study_name).first()
        sst = Substudy.query.filter_by(name=substudy_name, 
            study_id=st.id).first()
        sst_id = sst.id
        for t in v:
            log.debug("Adding [%i-%s]" % (sst_id, t))
            tissue=SubstudyTissue(substudy_id=sst_id,
                          tissue=t)
            db.session.add(tissue)
            db.session.commit()

def populate_database():
    reset_database()
    log.debug("Adding project")
    project = Project(name=settings.BIGQUERY_PROJECT)
    db.session.add(project)
    db.session.commit()
    log.debug("Adding dataset")
    dataset = Dataset(name=settings.BIGQUERY_DATASET, project_id=project.id)
    db.session.add(dataset)
    db.session.commit()
    tmeta = get_metadata_columns()
    add_studies_substudies()
    qb = QueryBuilder(table=None)
    for t in qb.list_tables():
        t.reload()
        tname = "%s:%s.%s" % (settings.BIGQUERY_PROJECT,
                              settings.BIGQUERY_DATASET, t.name)
        log.debug("Adding table [%s]" % (t.name))
        dt = add_table(t, dataset)
        add_columns(dt)
    add_tissues()

### tissue bit
