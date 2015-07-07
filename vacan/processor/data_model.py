#!/usr/bin/env python3

""" Contain database representation of all classes.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""
import datetime
import sqlalchemy.ext.declarative
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import functions as sqlfunctions

import vacan.config as cfg


Base = sqlalchemy.ext.declarative.declarative_base()


class RawVacancy(Base):
    """ Simple unprocessed vacancy. Contains name and html page. """
    __tablename__ = cfg.DB_VACANCIES_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    html = Column(TEXT)
    url = Column(TEXT)
    site = Column(TEXT)
    date = Column(DateTime)

    def __init__(self, name, html, url='NA', site='NA'):
        self.name = name
        self.html = html
        self.url = url
        self.site = site
        self.date = datetime.datetime.now()

    def __repr__(self):
        return 'RawVacancy: name={}, html_len={}, url={}'.format(
            self.name, len(self.html), self.url)


class OpenClosedSession(Session):
    """ This type of sessino can be used in with statement and it guarantees
        that session will commit on exit or error.
    """
    def __enter__(self):
        """ On enter in with """
        return self

    def __exit__(self, _type, value, traceback):
        """ On exit of with """
        self.commit()


class DBEngine(object):
    """ Handle database connections. """
    def __init__(self, db_name, mode='r', dbtype='mysql'):
        self.db_name = db_name
        self.dbtype = dbtype
        if mode == 'w' and dbtype == 'mysql':
            self.create_db()
        self.engine = sqlalchemy.create_engine(self.get_url())
        if (dbtype is not 'sqlite' and
            not sqlfunctions.database_exists(self.engine.url)):
            sqlfunctions.create_database(self.engine.url)
        self.sessionmaker = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(
                bind=self.engine, class_=OpenClosedSession))
        if mode == 'w':
            Base.metadata.create_all(self.engine)

    def get_session(self):
        """ Return session object, thread safe, can be used in with statement.
        """
        return self.sessionmaker()

    def dispose(self):
        """ Close all connection to database. """
        self.sessionmaker.close_all()
        self.engine.dispose()

    def create_db(self):
        """ Create database by name if not exists. """
        try:
            sqlfunctions.create_database(self.get_url())
        except sqlalchemy.exc.ProgrammingError:  # Db exists
            pass

    def drop_database(self):
        """ Drop database is exists. """
        self.dispose()
        if self.dbtype is not 'sqlite':
            sqlfunctions.drop_database(self.get_url())

    def get_url(self):
        """ Form url for db_name. """
        if self.dbtype == 'mysql':
            return '{}/{}?charset=utf8'.format(cfg.DB_PREFIXES[self.dbtype],
                                               self.db_name)
        elif self.dbtype == 'sqlite':
            url = '{}//{}'.format(cfg.DB_PREFIXES[self.dbtype], self.db_name)
            return url


class DBManager(object):
    """ DBManager TODO: add description. """
    def __init__(self, db_name, dbtype='mysql'):
        self.db_name = db_name
        self.dbengine = DBEngine(db_name, dbtype)

    def get_raw_vacs(self):
        """ Return list of raw vacancies from database. """
        with self.dbengine.get_session() as session:
            return list(session.query(RawVacancy))
