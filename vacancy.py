#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    save to database.
    run: ./market_analysis.py
    Also can process database data to csv file for futher analysis.
    run: ./market_analysis.py -p

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

# pylint: disable=F0401, R0903, R0201, R0921

import bs4
import datetime
import re
import pickle
import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy.ext.declarative import declarative_base
BASE = declarative_base()

import config as cfg


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
    proc_vac = Column(sqlalchemy.types.PickleType)
    date = Column(sqlalchemy.types.DateTime)

    def __init__(self, proc_vac, _time='now'):
        self.set_proc_vac(proc_vac)
        if _time == 'now':
            self.date = datetime.datetime.now()
        else:
            self.date = _time

    def get_proc_vac(self):
        if not self.proc_vac:
            return None
        return pickle.loads(self.proc_vac)

    def set_proc_vac(self, new_proc_vac):
        self.proc_vac = pickle.dumps(new_proc_vac)


class ProcessedVacancy():
    """ Processed vacancy. Contains name and tags."""
    # Possible tags:
    # Db: oragle, sql, mssql, postrgesql, db2
    # languages: c, ansi, ada
    # os: ios, linux, windows, unix,
    def __init__(self, vacancy, tags):
        """ Generate processed vacancy from vacancy. """
        self.name = vacancy.name
        soup = bs4.BeautifulSoup(vacancy.html)
        text = soup.get_text()
        text = text.lower()
        self.tags = {}
        for tag in tags:
            if tag[cfg.TAG_TEXT] in text:
                self.tags[tag[cfg.TAG_NAME]] = True
            else:
                self.tags[tag[cfg.TAG_NAME]] = False
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

