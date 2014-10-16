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
from sys import stdout, argv
import os
import tarfile

from config import *
from vacancy import *

title_filename = 'data/title.txt'
plot_filename_container = 'data/plot_name.txt'
labels_filename = 'data/pvac_labels.txt'
csv_filename = 'data/pvac.csv'


def prepare_db(db_name):
    """ Return sqlalchemy session. """
    engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
    Base.metadata.create_all(engine)
    session = sqlalchemy.orm.sessionmaker(bind=engine)()
    return session


def output_csv(session, file_name=csv_filename, tags=Tags, db_name=''):
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
    with open(title_filename, 'w') as label_fd:
        print(LABEL.format(CURRENT_SITE, stime), file=label_fd)
    with open(plot_filename_container, 'w') as plot_fd:
        print('plots/plot_{}_{}.png'.format(CURRENT_SITE, stime), file=plot_fd)


def compress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    compressed_fd = tarfile.open(db_name+'.tgz', 'w:gz')
    compressed_fd.add(db_name)
    compressed_fd.close()
    os.remove(db_name)


def uncompress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    compressed_fd = tarfile.open(db_name+'.tgz', 'r:gz')
    compressed_fd.extractall()
    os.remove(db_name + '.tgz')


def main():
    """ Just choose what to do: download or process. """

    def _download_to_db(db_name):
        """ Download all vacancies to database
            all for programmer.
        """
        session = prepare_db(db_name)
        site_parser = site_parser_factory('hh.ru')
        site_parser.get_all_vacancies(session)

    def _process_vacancies(db_name):
        """ Processing vacancies. """
        session = prepare_db(db_name)
        output_csv(session, db_name=db_name)

    def _plot():
        os.system('Rscript ./plot.R')

    os.chdir(os.path.dirname(argv[0]))
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
