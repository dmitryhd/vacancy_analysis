#!/usr/bin/env python3
# pylint: disable=E0001, R0921

""" Main module to download html pages from job sites, parse them and
    save to database.
    run: ./vacancy_processor.py -t -c
    Also can process database data to csv file for futher analysis.
    run: ./vacancy_processor.py -p -d <db_name>

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 04.12.2014
"""

import time
import datetime
import argparse
import sqlalchemy
from sys import argv
import os
import tarfile
import re

import site_parser as sp
import config as cfg
from data_model import BASE, Vacancy, ProcessedVacancy, ProcessedStatistics


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
        header += tag.title + '_min '
        columns.append([])
        header += tag.title + '_max '
        columns.append([])
    for pvac in proc_vacs:
        tag_index = 0
        for tag in tags:
            if pvac.tags[tag.name] and pvac.min_salary:
                columns[tag_index].append(pvac.min_salary)
            tag_index += 1
            if pvac.tags[tag.name] and pvac.max_salary:
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
            label = '"' + tag.name
            label += ' От. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=labels_fd, end='')
            tag_index += 1
            data = columns[tag_index]
            num = len(data)
            mean = int(sum(data))/len(data) if len(data) > 0 else 0
            mean = int(mean)
            label = '"' + tag.name
            label += ' До. Средн:{}, Вакансий:{}'.format(mean, num) + '" '
            print(label, file=labels_fd, end='')
            tag_index += 1

def get_time_by_filename(fname):
    seconds = re.search(r'(\d+)', fname)
    if not seconds:
        seconds = int(time.time())
    else:
        seconds = int(seconds.groups()[0])
    return seconds


def __create_csv(columns, header, csv_file_name):
    """ Output result to csv! """
    max_length = 0
    for column in columns:
        max_length = max(max_length, len(column))
    for column in columns:
        need_to_fill = max_length - len(column)
        column.extend(['NA']*need_to_fill)
    #save result
    csv_fd = open(csv_file_name, 'w')
    print(header, file=csv_fd)
    for i in range(max_length):
        out = ''
        for column in columns:
            out += str(column[i]) + ' '
        print(out, file=csv_fd)


def output_csv(header, columns, tags, file_name=cfg.CSV_FILENAME):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """

    __create_labels(columns, tags)
    __create_csv(columns, header, file_name)



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
    site = 'hh.ru'

    def _download_to_db(db_name, max_vac=cfg.MAXIM_NUMBER_OF_VACANCIES):
        """ Download all vacancies to database
            all for programmer.
        """
        session = prepare_db(db_name)
        site_parser = sp.site_parser_factory(site)
        site_parser.get_all_vacancies(session, max_vac)


    def _process_vacancies(db_name):
        """ Processing vacancies. """
        session = prepare_db(db_name)
        data_gather_time = get_time_by_filename(db_name)
        header, columns, pvacs = _load_vacancies_from_db(session, cfg.TAGS)
        output_csv(header, columns, cfg.TAGS)
        # create plot
        stime = datetime.datetime.fromtimestamp(
            data_gather_time).strftime("%Y-%m-%d")

        with open(cfg.TITLE_FILENAME, 'w') as label_fd:
            print(cfg.LABEL.format(site, stime), file=label_fd)
        with open(cfg.PLOT_FILENAME_CONTAINER, 'w') as plot_fd:
            print('plots/plot_{}_{}.png'.format(site, data_gather_time),
                  file=plot_fd)

        # output to stat db
        out_session = prepare_db(cfg.STAT_DB)
        proc_stat = ProcessedStatistics(pvacs, _time=data_gather_time)
        proc_stat.calculate_tag_bins()
        out_session.add(proc_stat)
        out_session.commit()


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
