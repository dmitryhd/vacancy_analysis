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
import time
import argparse
import sqlalchemy
from sys import stdout
import os
import tarfile

from config import *
from vacancy import *

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
            new_vacancy = get_vacancy(name, vacancy_html, link)
            vacancies.append(new_vacancy)
            session.add(new_vacancy)
            session.commit()
            stdout.write("\rdownloaded {} vacancy".format(new_vacancy.id))
            stdout.flush()
    try:
        link = soup.find_all('a', class_='b-pager__next-text')[1].attrs["href"]
    except IndexError:
        return None
    next_link = 'http://hh.ru' + link
    return next_link


def get_vacancy(name, html, link):
    """ Get base vacancy by name and html code of page. """
    new_html = ''
    soup = bs4.BeautifulSoup(html)
    # delete js
    [s.extract() for s in soup('script')]
    # delete style
    [s.extract() for s in soup('style')]
    res = soup.find('div', class_='b-important b-vacancy-info')
    if res:
        new_html += res.decode()
    res = soup.find('table', class_='l-content-2colums b-vacancy-container')
    if res:
        new_html += res.text
    #print(bs4.BeautifulSoup(new_html))
    return Vacancy(name, new_html, url=link, site='hh.ru')


def output_csv(session, file_name='data/pvac.csv', tags=Tags, db_name=''):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """
    labels_filename = 'data/pvac_labels.txt'
    proc_vacs = []
    # 1. load vacancies from db
    vacancies = session.query(Vacancy)
    total_cnt = 0
    for vac in vacancies:
        proc_vacs.append(ProcessedVacancy(vac, tags))
        total_cnt += 1
    header = ''
    columns = []
    for tag in tags:
        header += tag[tag_title] + '_min '
        columns.append([])
        header += tag[tag_title] + '_max '
        columns.append([])
    for pvac in proc_vacs:
        tag_index = 0
        for tag in tags:
            if pvac.tags[tag[tag_name]] and pvac.min_salary:
                columns[tag_index].append(pvac.min_salary)
            tag_index += 1
            if pvac.tags[tag[tag_name]] and pvac.max_salary:
                columns[tag_index].append(pvac.max_salary)
            tag_index += 1

    with open(labels_filename, 'w+') as fd:
        tag_index = 0
        for tag in tags:
            l = columns[tag_index]
            num = len(l)
            mean = int(sum(l))/len(l) if len(l) > 0 else 0
            mean = int(mean)
            label = '"' + tag[tag_name] + ' От. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=fd, end='')
            tag_index += 1
            l = columns[tag_index]
            num = len(l)
            mean = int(sum(l))/len(l) if len(l) > 0 else 0
            mean = int(mean)
            label = '"' + tag[tag_name] + ' До. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=fd, end='')
            tag_index += 1

    max_length = 0
    for column in columns:
        max_length = max(max_length, len(column))
    for column in columns:
        need_to_fill = max_length - len(column)
        column.extend(['NA']*need_to_fill)
    #save result
    csv_fd = open(file_name, 'w')
    print(header, file=csv_fd)
    for i in range(max_length):
        out = ''
        for column in columns:
            out += str(column[i]) + ' '
        print(out, file=csv_fd)

    time_in_sec = re.search(r'(\d)+', db_name)
    stime = ''
    if time_in_sec:
        time_in_sec = time.localtime(int(time_in_sec.group()))
        stime = time.strftime("%Y-%m-%d", time_in_sec)
    with open(label_file_name, 'w') as label_fd:
        print(LABEL.format(CURRENT_SITE, stime), file=label_fd)


def compress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    with open(db_name, 'rb') as db_fd:
        compressed_fd = tarfile.open(db_name+'.tgz', 'w:gz')
        compressed_fd.write(db_fd.read())
        compressed_fd.close()
    os.remove(db_name)


def uncompress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    with open(db_name, 'wb') as db_fd:
        compressed_fd = tarfile.open(db_name+'.tgz', 'r:gz')
        db_fd.write(compressed_fd.read())
        compressed_fd.close()
    os.remove(db_name + '.tgz')


def main():
    """ Just choose what to do: download or process. """

    def _download_to_db(db_name):
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

    def _process_vacancies(db_name):
        """ Processing vacancies. """
        session = prepare_db(db_name)
        output_csv(session, db_name=db_name)

    def _plot():
        os.system('Rscript ./plot.R')

    default_db_name = 'data/vac.db'
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db_name", type=str,
                        help="database name")
    parser.add_argument("-c", "--compress",
                        help="do compression",
                        action="store_true")
    parser.add_argument("-t", "--timestamp", help="add timestamp to database",
                    action="store_true")
    parser.add_argument("-p", "--process", help="run process on given db",
                    action="store_true")
    args = parser.parse_args()

    db_name = default_db_name
    if args.db_name:
        db_name = args.db_name
    if args.timestamp:
        db_name = 'data/vac_{}.db'.format(int(time.time()))
    print('using database:', db_name)

    if not args.process:
        _download_to_db(db_name)
    elif args.compress:
        uncompress_database(db_name)
    _process_vacancies(db_name)
    if args.compress:
        compress_database(db_name)
    _plot()


if __name__ == '__main__':
    main()
