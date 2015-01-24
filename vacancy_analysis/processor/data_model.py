#!/usr/bin/env python3

""" Contain database representation of all classes.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import bs4
import datetime
import time
import re
import pickle
pickle.DEFAULT_PROTOCOL = 3
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text, PickleType, DateTime

import vacancy_analysis.processor.processor_config as cfg


Base = sqlalchemy.ext.declarative.declarative_base()


class RawVacancy(Base):
    """ Simple unprocessed vacancy. Contains name and html page. """
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    name = Column(String(cfg.DB_MAX_STRING_LEN))
    html = Column(Text)
    url = Column(Text)
    site = Column(String(cfg.DB_MAX_STRING_LEN))
    date = Column(DateTime)

    def __init__(self, name, html, url='NA', site='NA'):
        self.name = name
        self.html = html
        self.url = url
        self.site = site
        self.date = datetime.datetime.now()

    def __repr__(self):
        return 'RawVacancy: id={}, name={}, html_len={}'.format(self.id,
                                                                self.name,
                                                                len(self.html))

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


def open_db(db_name, mode='w'):
    """ Return sqlalchemy session. Modes of operation: Read, Write [r, w]. """
    engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
    if mode != 'r':
        Base.metadata.create_all(engine)
    return sqlalchemy.orm.sessionmaker(bind=engine)()


def process_vacancies_from_db(session, tags):
    """ Get list of processed vacancies from database of raw vacancies."""
    proc_vacs = []
    vacancies = session.query(RawVacancy)
    for vac in vacancies:
        proc_vacs.append(ProcessedVacancy(vac, tags))
    return proc_vacs
