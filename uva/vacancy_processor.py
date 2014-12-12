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


def get_time_by_filename(fname):
    seconds = re.search(r'(\d+)', fname)
    if not seconds:
        seconds = int(time.time())
    else:
        seconds = int(seconds.groups()[0])
    return seconds


def compress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    os.system('tar czf {} {}'.format(db_name + '.tgz', db_name))
    os.remove(db_name)


def uncompress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    os.system('tar xzf {} '.format(db_name))
    os.remove(db_name)
    return db_name.replace('.tgz', '')


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

    if args.compress and args.process:
        args.db_name = uncompress_database(args.db_name)
    raw_vac_db = open_db(args.db_name)
    if not args.process:
        site_parser = sp.site_parser_factory(site)
        site_parser.get_all_vacancies(raw_vac_db, args.num_vac)
    # Process vacs:
    current_tags = cfg.TAGS
    proc_vac_db = open_db(args.db_name)
    processed_vacancies = process_vacancies_from_db(raw_vac_db, current_tags)
    # Save processed vacancies to statistics database.
    stat_db = open_db(cfg.STAT_DB)
    gather_time_sec = get_time_by_filename(args.db_name)
    proc_stat = ProcessedStatistics(processed_vacancies, gather_time_sec)
    proc_stat.calculate_all()
    stat_db.add(proc_stat)
    stat_db.commit()

    if args.compress:
        compress_database(args.db_name)


if __name__ == '__main__':
    main()
