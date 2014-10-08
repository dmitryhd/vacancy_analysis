#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    save to database.
    run: ./market_analysis.py
    Also can process database data to csv file for futher analysis.
    run: ./market_analysis.py -p

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import bs4
import requests
import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy.ext.declarative import declarative_base
import sys
import re
import time


Base = declarative_base()
BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
MAXIM_NUMBER_OF_PAGES = 1000


def get_url(url):
    """ Get HTML page by its URL. """
    session = requests.Session()
    page = session.get(url).text
    return page


def prepare_db(db_name):
    """ Return sqlalchemy session. """
    engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
    Base.metadata.create_all(engine)
    session = sqlalchemy.orm.sessionmaker(bind=engine)()
    return session


def get_vacancies_on_page(url, vacancies, session):
    """ Download all vacancies from page and return link to next page. """
    page = get_url(url)
    soup = bs4.BeautifulSoup(page)
    for vacancy in soup.find_all('div', class_='searchresult__name'):
        name = vacancy.string
        if name is not None:
            link = vacancy.find_all('a')[0].attrs["href"]
            vacancy_html = get_url(link)
            new_vacancy = Vacancy(name, vacancy_html)
            vacancies.append(new_vacancy)
            session.add(new_vacancy)
            session.commit()
            print(new_vacancy)
    try:
        link = soup.find_all('a', class_='b-pager__next-text')[1].attrs["href"]
    except IndexError:
        return None
    next_link = 'http://hh.ru' + link
    return next_link


class Vacancy(Base):
    """ Simple unprocessed vacancy. Contains name and html page. """
    __tablename__ = 'vacancy'
    id = Column(sqlalchemy.types.Integer, primary_key=True)
    name = Column(sqlalchemy.types.String(100))
    html = Column(sqlalchemy.types.Text)

    def __init__(self, name, html):
        self.name = name
        self.html = html

    def __repr__(self):
        return 'Vacancy: id={}, name={}, html={}'.format(self.id,
                                                         self.name,
                                                         len(self.html))

class Tag():
    """ Contain category for vacancy. """
    def __init__(self, name, text=None, title=None):
        self.name = name  # General name
        self.text = text if text else self.name  # Text to search for
        self.title = title if title else self.text  # Title for R


class ProcessedVacancy(Base):
    """ Processed vacancy. Contains name, 2 parts of page, and skills."""
    __tablename__ = 'proc_vacancy'
    id = Column(sqlalchemy.types.Integer, primary_key=True)
    name = Column(sqlalchemy.types.String(100))
    imp_html = Column(sqlalchemy.types.Text)
    short_html = Column(sqlalchemy.types.Text)
    max_salary = Column(sqlalchemy.types.Integer)
    min_salary = Column(sqlalchemy.types.Integer)
    # Keywords in text of vacancy.
    # languages
    skills = ['c++',
              'python',
              'perl',
              'ruby',
              'bash',
              'java',
              'javascript',
              '1c',
              'sap',
              'php',
             ]
    # Possible tags: 
    # Db: oragle, sql, mssql, postrgesql, db2 
    # languages: c, ansi, ada
    # os: ios, linux, windows, unix, 
    # manager, руководитель, аналитик, стажер, senior, администратор
    def __init__(self):
        """ Fill skills. """
        self.has_skills = {skill:False for skill in self.skills}

    def __repr__(self):
        res = 'ProcVacancy: id={}, name={}\n'.format(self.id, self.name)
        res += 'imp html ---------\n'
        res += self.imp_html
        res += '\nshort html ---------\n'
        res += self.short_html
        return res

def set_tags_to_vacancy(vac, tags):
    """ Generate processed vacancy from vacancy. """
    pvac = ProcessedVacancy()
    pvac.name = vac.name
    soup = bs4.BeautifulSoup(vac.html)
    text = soup.getText("\n")
    text = text.lower()
    pvac.tags = {}
    for tag in tags:
        if tag.text in text:
            pvac.tags[tag.name] = True
        else:
            pvac.tags[tag.name] = False
    return pvac

def get_vacancy(name, html):
    """ Get base vacancy by name and html code of page. """
    return Vacancy(name, html)


def get_salary(vac):
    """ Get min and max salary from vacancy. """
    soup = bs4.BeautifulSoup(vac.html)
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

def process_vacancies(session, file_name='data/pvac.csv'):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """
    proc_vacs = []
    # 1. load vacancies from db
    vacancies = session.query(Vacancy)
    error_cnt = 0
    total_cnt = 0
    for vac in vacancies:
        # 2. get maximum and minimum salary
        min_salary, max_salary = get_salary(vac)
        pvac.min_salary = min_salary
        pvac.max_salary = max_salary
        # 3. get Skills:
        pvac = set_tags_to_vacancy(vac)

    #4~~ export to csv
    csv_fd = open(file_name, 'w')
    headers = 'min_salary; max_salary'
    for skill in ProcessedVacancy.skills:
        headers += '; {}'.format(skill)
    print(headers, file=csv_fd)
    for pvac in proc_vacs:
        vac_str = ''
        if pvac.min_salary is None:
            vac_str += 'Null; '
        else:
            vac_str += str(pvac.min_salary) + '; '
        if pvac.max_salary is None:
            vac_str += 'Null'
        else:
            vac_str += str(pvac.max_salary)
        for skill in pvac.skills:
            vac_str += '; {}'.format(int(pvac.has_skills[skill]))
        print(vac_str, file=csv_fd)
    # 5. get location of vacancy
    # 6. categorizing by company
    print('\nFinised processing. Parsing errors = {}, total = {}.'.format(
        error_cnt,
        total_cnt))


def main():
    """ Just choose what to do: download or process. """

    def __download_to_db(db_name):
        """ Download all vacancies to database
            all for programmer.
        """
        session = prepare_db(db_name)
        vacancies = []
        next_link = BASE_URL
        for i in range(MAXIM_NUMBER_OF_PAGES):
            next_link = get_vacancies_on_page(next_link, vacancies, session)
            if next_link == None:
                break

    def __process_vacancies(db_name):
        """ Processing vacancies. """
        session = prepare_db(db_name)
        process_vacancies(session)

    if len(sys.argv) == 2 and sys.argv[1] == '-t':
        default_db_name = 'data/hh_{}.db'.format(int(time.time()))
    elif len(sys.argv) == 3 and sys.argv[2] == '-t':
        default_db_name = 'data/hh_{}.db'.format(int(time.time()))
    elif len(sys.argv) == 3 and sys.argv[2] != '-t':
        default_db_name = sys.argv[2]
    else:
        default_db_name = 'data/vac.db'

    print(default_db_name)

    if len(sys.argv) == 1:
        __download_to_db(default_db_name)
        __process_vacancies(default_db_name)
    elif sys.argv[1] == '-p':
        __process_vacancies(default_db_name)
    elif sys.argv[1] == '-t':
        __download_to_db(default_db_name)
        __process_vacancies(default_db_name)



if __name__ == '__main__':
    main()
