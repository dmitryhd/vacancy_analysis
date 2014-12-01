#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    save to database.
    run: ./vacancy_processor.py -t -c
    Also can process database data to csv file for futher analysis.
    run: ./vacancy_processor.py -p -d <db_name>

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import time
import argparse
import sqlalchemy
from sys import argv
import os
import tarfile
import re


import site_parser as sp
import config as cfg
from vacancy import BASE, Vacancy, ProcessedVacancy

# pylint: disable=E0001, R0921

def prepare_db(db_name):
    """ Return sqlalchemy session. """
    engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
    BASE.metadata.create_all(engine)
    session = sqlalchemy.orm.sessionmaker(bind=engine)()
    return session


def _load_vacancies_from_db(session, tags):
    """ Return header, columns of data. """
    proc_vacs = []
    vacancies = session.query(Vacancy)
    for vac in vacancies:
        proc_vacs.append(ProcessedVacancy(vac, tags))
    header = ''
    columns = []
    for tag in tags:
        header += tag[cfg.TAG_TITLE] + '_min '
        columns.append([])
        header += tag[cfg.TAG_TITLE] + '_max '
        columns.append([])
    for pvac in proc_vacs:
        tag_index = 0
        for tag in tags:
            if pvac.tags[tag[cfg.TAG_NAME]] and pvac.min_salary:
                columns[tag_index].append(pvac.min_salary)
            tag_index += 1
            if pvac.tags[tag[cfg.TAG_NAME]] and pvac.max_salary:
                columns[tag_index].append(pvac.max_salary)
            tag_index += 1
    return header, columns, proc_vacs


def __create_labels(columns, tags):
    """ Write file, creating headers for plot. """
    with open(cfg.LABELS_FILENAME, 'w+') as labels_fd:
        tag_index = 0
        for tag in tags:
            data = columns[tag_index]
            num = len(data)
            mean = int(sum(data))/len(data) if len(data) > 0 else 0
            mean = int(mean)
            label = '"' + tag[cfg.TAG_NAME]
            label += ' От. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=labels_fd, end='')
            tag_index += 1
            data = columns[tag_index]
            num = len(data)
            mean = int(sum(data))/len(data) if len(data) > 0 else 0
            mean = int(mean)
            label = '"' + tag[cfg.TAG_NAME]
            label += ' До. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=labels_fd, end='')
            tag_index += 1


def __create_csv(columns, header, file_name, db_name):
    """ Output result to csv! """
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

    time_in_sec = re.search(r'(\d+)', db_name)
    stime = ''
    if not time_in_sec:
        time_in_sec = time.localtime()
        stime = time.strftime("%Y-%m-%d", time_in_sec)
    else:
        time_in_sec = int(time_in_sec.groups()[0])
        print('time_in_sec:', time_in_sec)
        stime = time.strftime("%Y-%m-%d", time.localtime(time_in_sec))
        print('stime:', stime)

    with open(cfg.TITLE_FILENAME, 'w') as label_fd:
        print(cfg.LABEL.format(cfg.CURRENT_SITE, stime), file=label_fd)
    with open(cfg.PLOT_FILENAME_CONTAINER, 'w') as plot_fd:
        print('plots/plot_{}_{}.png'.format(cfg.CURRENT_SITE, stime),
              file=plot_fd)


def output_csv(session, tags, file_name=cfg.CSV_FILENAME, db_name=''):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """

    header, columns, pvacs = _load_vacancies_from_db(session, tags)
    __create_labels(columns, tags)
    __create_csv(columns, header, file_name, db_name)


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

    def _download_to_db(db_name, max_vac=cfg.MAXIM_NUMBER_OF_VACANCIES):
        """ Download all vacancies to database
            all for programmer.
        """
        session = prepare_db(db_name)
        site_parser = sp.site_parser_factory('hh.ru')
        site_parser.get_all_vacancies(session, max_vac)


    def _process_vacancies(db_name):
        """ Processing vacancies. """
        session = prepare_db(db_name)
        output_csv(session, tags=cfg.TAGS, db_name=db_name)

    def _plot():
        """ Create plot png. """
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
    parser.add_argument("-n", "--num_vac", help="none", type=int)
    args = parser.parse_args()

    db_name = default_db_name
    if args.db_name:
        db_name = args.db_name
    if args.timestamp:
        db_name = 'data/vac_{}.db'.format(int(time.time()))
    print('using database:', db_name)

    if not args.process:
        if args.num_vac:
            _download_to_db(db_name, args.num_vac)
        else:
            _download_to_db(db_name)
    elif args.compress:  # if process and compress
        uncompress_database(db_name)
    _process_vacancies(db_name)
    if args.compress:
        compress_database(db_name)
    _plot()


if __name__ == '__main__':
    main()
