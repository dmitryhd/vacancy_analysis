#!/usr/bin/env python3

""" Contain database representation of all classes.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import bs4
import datetime
import time
import re
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.dialects.mysql import TEXT

import vacan.common.processor_config as cfg


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


class ProcessedVacancy():
    """ Processed vacancy. Contains name, tags and salary."""
    def __init__(self, vacancy, tags):
        """ Generate processed vacancy from vacancy. """
        self.name = vacancy.name
        soup = bs4.BeautifulSoup(vacancy.html)
        text = soup.get_text()
        self.min_salary, self.max_salary = self.get_salary(soup)
        text = text.lower()
        self.tags = {}
        for tag in tags:
            if tag.text in text:
                self.tags[tag.name] = True
            else:
                self.tags[tag.name] = False

    def get_salary(self, soup):
        """ Get min and max salary from vacancy. """
        # TODO: extract method
        # TODO: extract data
        res = soup.find('td', class_='l-content-colum-1 b-v-info-content')
        if not res is None:
            digits = re.search(r'от\s+(\d+)\s+(\d*)', res.text)
            if digits:
                min_salary = int(''.join(digits.groups()))
            else:
                min_salary = None
            digits = re.search(r'до\s+(\d+)\s+(\d*)', res.text)
            if digits:
                max_salary = int(''.join(digits.groups()))
            else:
                max_salary = None
            return min_salary, max_salary
        return None, None

    def __repr__(self):
        out = '{} {} {}'.format(self.name, self.min_salary, self.max_salary)
        out += '\ntags:' + str(self.tags)
        return out


class DatabaseManager(object):
    def __init__(self, db_name, mode='r'):
        self.db_name = db_name
        engine = create_mysql_db(db_name)
        engine.dispose()
        self.engine = sqlalchemy.create_engine(cfg.DB_PREFIX + db_name)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        if mode == 'w':
            Base.metadata.create_all(self.engine)
    
    def __enter__(self):
        return self.sessionmaker()

    def __exit__(self, exc_type, exc_value, traceback):
        self.engine.dispose()

    def get_session(self):
        return self.sessionmaker()

    def dispose(self):
        self.engine.dispose()

def create_mysql_db(db_name):
    engine = sqlalchemy.create_engine(cfg.DB_PREFIX, echo=False) # connect to server
    try:
        engine.execute("CREATE DATABASE IF NOT EXISTS {};".format(db_name)) 
    except sqlalchemy.exc.DatabaseError:
        pass
    engine.execute("USE " + db_name)
    return engine


def delete_mysql_db(db_name):
    engine = sqlalchemy.create_engine(cfg.DB_PREFIX, echo=False)
    engine.execute('DROP DATABASE {};'.format(db_name))


def open_db(db_name, mode='w', echo=False):
    """ Return sqlalchemy session. Modes of operation: Read, Write [r, w]. """
    if cfg.DB_ENGINE == 'sqlite':
        engine = sqlalchemy.create_engine(cfg.DB_PREFIX + db_name, echo=echo)
    else:
        engine = create_mysql_db(db_name)
    if mode != 'r':
        Base.metadata.create_all(engine)
    return sqlalchemy.orm.sessionmaker(bind=engine)()


def process_vacancies(raw_vacs, tags):
    return [ProcessedVacancy(vac, tags) for vac in raw_vacs]
    

def process_vacancies_from_db(session, tags):
    """ Get list of processed vacancies from database of raw vacancies."""
    return process_vacancies(list(session.query(RawVacancy)), tags)


