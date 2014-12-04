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
from data_model import Vacancy, ProcessedVacancy, ProcessedStatistics
import data_model as dm


def create_csv_data(proc_vacs, tags):
    """ Get header and columns of values of equal lengths
        from processed vacancies.
    """
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
    return header, columns


def get_time_by_filename(fname):
    """ Return timestamp, encoded in filename. """
    seconds = re.search(r'(\d+)', fname)
    if not seconds:
        seconds = int(time.time())
    else:
        seconds = int(seconds.groups()[0])
    return seconds


def output_csv(processed_vacancies, tags, csv_file_name=cfg.CSV_FILENAME):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """
    header, columns = create_csv_data(processed_vacancies, tags)
    # Create labels.
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

    # Output result to csv.
    max_length = 0
    for column in columns:
        max_length = max(max_length, len(column))
    for column in columns:
        need_to_fill = max_length - len(column)
        column.extend(['NA']*need_to_fill)
    csv_fd = open(csv_file_name, 'w')
    print(header, file=csv_fd)
    for i in range(max_length):
        out = ''
        for column in columns:
            out += str(column[i]) + ' '
        print(out, file=csv_fd)


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


def plot(data_gather_time, site):
    """ Create plot png. Get time in seconds."""
    # Create config files for R script, which will plot data to image.
    stime = datetime.datetime.fromtimestamp(
        data_gather_time).strftime("%Y-%m-%d")

    with open(cfg.TITLE_FILENAME, 'w') as label_fd:
        print(cfg.LABEL.format(site, stime), file=label_fd)
    with open(cfg.PLOT_FILENAME_CONTAINER, 'w') as plot_fd:
        print('plots/plot_{}_{}.png'.format(site, data_gather_time),
              file=plot_fd)
    # Run R script.
    os.system('Rscript ./plot.R')


def main():
    """ Just choose what to do: download or process. """

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

    site = 'hh.ru'
    max_vac = args.num_vac if args.num_vac else cfg.MAXIM_NUMBER_OF_VACANCIES
    if not args.process:
        session = dm.open_db(db_name, 'w')
        site_parser = sp.site_parser_factory(site)
        site_parser.get_all_vacancies(session, max_vac)

    elif args.compress:  # if process and compress
        uncompress_database(db_name)

    # Process vacancies to csv.
    raw_vac_db = dm.open_db(db_name, 'r')
    proc_vacs = dm.process_vacancies_from_db(raw_vac_db, cfg.TAGS)
    output_csv(proc_vacs, cfg.TAGS)
    # Save processed vacancies to statistics database.
    out_session = dm.open_db(cfg.STAT_DB, 'w')
    data_gather_time = get_time_by_filename(db_name)
    proc_stat = ProcessedStatistics(proc_vacs, _time=data_gather_time)
    proc_stat.calculate_tag_bins()
    out_session.add(proc_stat)
    out_session.commit()

    if args.compress:
        compress_database(db_name)
    plot(data_gather_time, site)


if __name__ == '__main__':
    main()
