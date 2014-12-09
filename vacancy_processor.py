#!/usr/bin/env python3
# pylint: disable=E0001, R0921

""" Main module to download html pages fro hh.ru, parse them and
    save to database.
    run: ./vacancy_processor.py -t -c
    Also can process database data to csv file for futher analysis.
    run: ./vacancy_processor.py -p -d <db_name>

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import time
from datetime import datetime
import argparse
import sqlalchemy
import sys
import os
import tarfile
import re

import site_parser as sp
import config as cfg
from data_model import BASE, Vacancy, ProcessedVacancy, ProcessedStatistics
from data_model import process_vacancies_from_db, open_db


def get_csv_header_and_columns(proc_vacs, tags):
    """ Return header, columns of data. """
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


def create_plot_labels(columns, tags):
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


def output_csv(pvacs, tags, csv_file_name=cfg.CSV_FILENAME):
    """ Generate csv file with vacancy name, minimum and maximum salary
        anb information about programming language.
    """
    header, columns = get_csv_header_and_columns(pvacs, tags)
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


def plot(gather_time_sec, site):
    """ Create plot png. """
    gather_time_str = datetime.fromtimestamp(gather_time_sec).strftime(
        "%Y-%m-%d")

    with open(cfg.TITLE_FILENAME, 'w') as label_fd:
        print(cfg.LABEL.format(site, gather_time_str), file=label_fd)
    with open(cfg.PLOT_FILENAME_CONTAINER, 'w') as plot_fd:
        print('plots/plot_{}_{}.png'.format(
            site, gather_time_sec), file=plot_fd)
    import subprocess;
    output = subprocess.check_output('Rscript ./plot.R',
                                     stderr=subprocess.DEVNULL,
                                     shell=True);

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db_name", type=str,
                        default='data/vac.db',
                        help="database name")
    parser.add_argument("-c", "--compress",
                        help="do compression",
                        action="store_true")
    parser.add_argument("-t", "--timestamp", help="add timestamp to database",
                        action="store_true")
    parser.add_argument("-p", "--process", help="run process on given db",
                        action="store_true")
    parser.add_argument("-n", "--num_vac", help="none",
                        default=cfg.MAXIM_NUMBER_OF_VACANCIES, type=int)
    args = parser.parse_args()
    if args.timestamp:
        args.db_name = 'data/vac_{}.db'.format(int(time.time()))
    return args


def main():
    """ Download vacancies from site then process them to statistics
        and plot.
    """
    site = 'hh.ru'
    os.chdir(os.path.dirname(sys.argv[0]))
    args = parse_args()

    raw_vac_db = open_db(args.db_name)
    if not args.process:
        site_parser = sp.site_parser_factory(site)
        site_parser.get_all_vacancies(raw_vac_db, args.num_vac)
    elif args.compress:  # if process and compress
        uncompress_database(args.db_name)
    # Process vacs:
    current_tags = cfg.TAGS
    proc_vac_db = open_db(args.db_name)
    processed_vacancies = process_vacancies_from_db(raw_vac_db, current_tags)
    header, columns = get_csv_header_and_columns(processed_vacancies,
                                                 current_tags)
    output_csv(processed_vacancies, current_tags)
    # Prep for plot
    create_plot_labels(columns, current_tags)
    # Save processed vacancies to statistics database.
    stat_db = open_db(cfg.STAT_DB)
    gather_time_sec = get_time_by_filename(args.db_name)
    proc_stat = ProcessedStatistics(processed_vacancies, gather_time_sec)
    proc_stat.calculate_tag_bins()
    stat_db.add(proc_stat)
    stat_db.commit()

    if args.compress:
        compress_database(args.db_name)
    plot(gather_time_sec, site)


if __name__ == '__main__':
    main()
