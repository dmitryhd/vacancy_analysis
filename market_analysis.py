#!/usr/bin/env python3

import bs4
import requests
import sqlalchemy
from sqlalchemy.types import *
from sqlalchemy.schema import *
from sqlalchemy.ext.declarative import declarative_base
import sys
import re
Base = declarative_base()


def get_url(url):
    """ Get HTML page by its URL """
    s = requests.Session()
    page = s.get(url).text
    return page

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
    next_link = 'http://hh.ru' + soup.find_all('a', class_='b-pager__next-text')[1].attrs["href"]
    #print('next = ', next_link)
    return next_link


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    name =  Column(String(100))
    html =  Column(Text)

    def __init__(self, name, html):
        self.name = name
        self.html = html

    def __repr__(self):
        return 'Vacancy: id={}, name={}, html={}'.format(self.id, self.name, len(self.html))

class ProcessedVacancy(Base):
    __tablename__ = 'proc_vacancy'
    id = Column(Integer, primary_key=True)
    name =  Column(String(100))
    imp_html = Column(Text)
    short_html = Column(Text)
    max_salary = Column(Integer)
    min_salary = Column(Integer)
    skills = ['c++',
              'python',
              'perl',
              'ruby',
              'bash',
              'java',
              'javascript',
              '1c',
              'sap',
              'matlab',
              'php',
              'net'
              ]
    def __init__(self):
        self.has_skills = {skill:False for skill in self.skills}

    def __repr__(self):
        res = 'ProcVacancy: id={}, name={}\n'.format(self.id, self.name)
        res += 'imp html ---------\n'
        res += self.imp_html
        res += '\nshort html ---------\n'
        res += self.short_html
        return res


def process_vacancies(session, file_name='data/pvac.csv'):

    print('Processing vacancies')
    proc_vacs = []
    # 1. load vacancies from db
    vacancies = session.query(Vacancy)
    # 2. get content of all vacancy divs
    error_cnt = 0
    total_cnt = 0
    for vac in vacancies:
        total_cnt += 1
        pvac = ProcessedVacancy()
        pvac.name = vac.name
        soup = bs4.BeautifulSoup(vac.html)
        res = soup.find('div', class_='b-important b-vacancy-info')
        if res is None:
            error_cnt += 1
            continue
        pvac.imp_html = res.decode()
        res = soup.find('table', class_='l-content-2colums b-vacancy-container')
        if res is None:
            error_cnt += 1
            continue
        pvac.short_html = res.text
        proc_vacs.append(pvac)
        #print('')
        #print(pvac)
    # 3. get maximum and minimum salary
    for pvac in proc_vacs:
        soup = bs4.BeautifulSoup(pvac.imp_html)
        res = soup.find('td', class_='l-content-colum-1 b-v-info-content')
        if not res is None:
            digits = re.search(r'от\s+(\d+)\s+(\d*)', res.text)
            if digits:
                pvac.min_salary = int(''.join(digits.groups()))
            else:
                pvac.min_salary = None
            digits = re.search(r'до\s+(\d+)\s+(\d*)', res.text)
            if digits:
                pvac.max_salary = int(''.join(digits.groups()))
            else:
                pvac.max_salary = None
    # 4. get Skills:
    # 4.1 clear all tags, normalize and leave only english letters and digits >=3
    # 4.2 frequency dict for all vacancies skills.
    # 4.3 make database of skills
    # 4.4 mark every vacancy for skill
    # 4~ temporary - use preset skills
    for pvac in proc_vacs:
        soup = bs4.BeautifulSoup(pvac.short_html)
        text = soup.getText("\n")
        text = text.lower()
        for skill in pvac.skills:
            if skill in text:
                pvac.has_skills[skill] = True
        print('short vac: {} min={} max={} skills={}'.format(pvac.name, pvac.min_salary, 
                                                             pvac.max_salary, pvac.has_skills))

    #4~~ export to csv
    fd = open(file_name, 'w')
    headers = 'min_salary; max_salary'
    for skill in ProcessedVacancy.skills:
        headers += '; {}'.format(skill)
    print(headers, file=fd)
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
        print(vac_str, file=fd)
    # 5. get location of vacancy
    # 6. categorizing by company
    print('\n end. errors = {}, total = {}'.format(error_cnt, total_cnt))



def prepare_db(db_name='data/vac.db'):
    engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
    Base.metadata.create_all(engine)
    session = sqlalchemy.orm.sessionmaker(bind=engine)()
    return session

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Download all vacancies to database
        # all for programmer
        session = prepare_db()
        vacancies = []
        base_url = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
        next_link = base_url
        for i in range(200):
            next_link = get_vacancies_on_page(next_link, vacancies, session)
    elif sys.argv[1] == '-p':
        # Processing vacancies
        session = prepare_db()
        process_vacancies(session)
