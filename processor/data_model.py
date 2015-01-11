#!/usr/bin/env python3
# pylint: disable=F0401, R0903, R0201, R0921

""" Contain database representation of all classes.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import bs4
import datetime
import time
import re
import pickle
import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy.ext.declarative import declarative_base

import config as cfg

pickle.DEFAULT_PROTOCOL = 3
BASE = declarative_base()

class Vacancy(BASE):
    """ Simple unprocessed vacancy. Contains name and html page. """
    __tablename__ = 'vacancy'
    id = Column(sqlalchemy.types.Integer, primary_key=True)
    name = Column(sqlalchemy.types.String(100))
    html = Column(sqlalchemy.types.Text)
    url = Column(sqlalchemy.types.Text)
    date = Column(sqlalchemy.types.DateTime)
    site = Column(sqlalchemy.types.String(100))

    def __init__(self, name, html, url='NA', site='NA'):
        self.name = name
        self.html = html
        self.url = url
        self.date = datetime.datetime.now()
        self.site = site

    def __repr__(self):
        return 'Vacancy: id={}, name={}, html={}'.format(self.id,
                                                         self.name,
                                                         len(self.html))

class ProcessedStatistics(BASE):
    """ Table entry for vacancy statistics for certain time. """
    __tablename__ = 'statistics'
    id = Column(sqlalchemy.types.Integer, primary_key=True)
    date = Column(sqlalchemy.types.Integer)
    proc_vac = Column(sqlalchemy.types.PickleType)
    tag_bins = Column(sqlalchemy.types.PickleType)
    mean_max_salary = Column(sqlalchemy.types.PickleType)
    mean_min_salary = Column(sqlalchemy.types.PickleType)

    def __init__(self, proc_vac, _time='now'):
        self.set_proc_vac(proc_vac)
        if _time == 'now':
            self.date = int(time.time())
        else:
            self.date = _time

    def get_proc_vac(self):
        """ Decapsulate pickle. """
        if not self.proc_vac:
            return None
        return pickle.loads(self.proc_vac)

    def get_tag_bins(self):
        """ Decapsulate pickle. """
        if not self.tag_bins:
            return None
        return pickle.loads(self.tag_bins)

    def set_proc_vac(self, new_proc_vac):
        """ Encapsulate to pickle. """
        self.proc_vac = pickle.dumps(new_proc_vac)

    def calculate_tag_bins(self, tags=cfg.TAGS):
        """ Calculate statistics for number of vacancies by bins. """
        pvacancies = self.get_proc_vac()
        tag_bins = {tag.name: 0 for tag in tags}
        for pvac in pvacancies:
            for tag_name, tag_val in pvac.tags.items():
                tag_bins[tag_name] += tag_val
        print('tag_bins:', tag_bins)
        self.tag_bins = pickle.dumps(tag_bins)

    def calculate_mean_max_salary(self, tags=cfg.TAGS):
        """ Return list of mean values of maximum salary by tags. """
        pvacancies = self.get_proc_vac()
        salary_by_tag = {tag.name: [0, 0] for tag in tags}  # [counter, salary]
        for pvac in pvacancies:
            if not pvac.max_salary:
                continue
            for tag_name, tag_val in pvac.tags.items():
                if tag_val:
                    salary_by_tag[tag_name][0] += 1
                    salary_by_tag[tag_name][1] += pvac.max_salary
        for tag_name in salary_by_tag.keys():
            cnt, sum_salary = salary_by_tag[tag_name]
            salary_by_tag[tag_name] = sum_salary / cnt if cnt else 0
        self.mean_max_salary = pickle.dumps(salary_by_tag)
        print('salary by tag:', salary_by_tag)

    def get_mean_max_salary(self):
        if not self.mean_max_salary:
            return None
        return pickle.loads(self.mean_max_salary)

    def calculate_mean_min_salary(self, tags=cfg.TAGS):
        """ Return list of mean values of maximum salary by tags. """
        pvacancies = self.get_proc_vac()
        salary_by_tag = {tag.name: [0, 0] for tag in tags}  # [counter, salary]
        for pvac in pvacancies:
            if not pvac.min_salary:
                continue
            for tag_name, tag_val in pvac.tags.items():
                if tag_val:
                    salary_by_tag[tag_name][0] += 1
                    salary_by_tag[tag_name][1] += pvac.min_salary
        for tag_name in salary_by_tag.keys():
            cnt, sum_salary = salary_by_tag[tag_name]
            salary_by_tag[tag_name] = sum_salary / cnt if cnt else 0
        print('salary by tag:', salary_by_tag)
        self.mean_min_salary = pickle.dumps(salary_by_tag)

    def get_mean_min_salary(self):
        if not self.mean_min_salary:
            return None
        return pickle.loads(self.mean_min_salary)


    def __repr__(self):
        return 'Statistics: {}'.format(self.date)

    def calculate_all(self):
        self.calculate_tag_bins()
        self.calculate_mean_max_salary()
        self.calculate_mean_min_salary()


class ProcessedVacancy():
    """ Processed vacancy. Contains name, tags and salary."""
    def __init__(self, vacancy, tags):
        """ Generate processed vacancy from vacancy. """
        self.name = vacancy.name
        soup = bs4.BeautifulSoup(vacancy.html)
        text = soup.get_text()
        text = text.lower()
        self.tags = {}
        for tag in tags:
            if tag.text in text:
                self.tags[tag.name] = True
            else:
                self.tags[tag.name] = False
        self.min_salary, self.max_salary = self.get_salary(soup)

    def get_salary(self, soup):
        """ Get min and max salary from vacancy. """
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
        BASE.metadata.create_all(engine)
    return sqlalchemy.orm.sessionmaker(bind=engine)()


def process_vacancies_from_db(session, tags):
    """ Get list of processed vacancies from database of raw vacancies."""
    proc_vacs = []
    vacancies = session.query(Vacancy)
    for vac in vacancies:
        proc_vacs.append(ProcessedVacancy(vac, tags))
    return proc_vacs
