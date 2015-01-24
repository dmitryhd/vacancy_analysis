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
import sys
import os

import vacancy_analysis.common.utility as util
import vacancy_analysis.common.tag_config as tag_cfg
import vacancy_analysis.processor.site_parser as sp
import vacancy_analysis.processor.processor_config as cfg
import vacancy_analysis.processor.data_model as dm
from vacancy_analysis.processor.statistics import ProcessedStatistics


def parse_args():
    """ Process command line arguments. """
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
        args.db_name = '/opt/vacan/data/vac_{}.db'.format(int(time.time()))
    return args


def main():
    """ Download vacancies from site then process them to statistics
        and plot.
    """
    site = 'hh.ru'
    args = parse_args()

    # Decompress db if needed
    if args.compress and args.process:
        args.db_name = util.uncompress_database(args.db_name)
    # Save raw vac to database
    print(args.db_name)
    print(os.getcwd())
    raw_vac_db = dm.open_db(args.db_name)
    if not args.process:
        site_parser = sp.site_parser_factory(site)
        site_parser.get_all_vacancies(raw_vac_db, args.num_vac)
    # Process vacs:
    processed_vacancies = dm.process_vacancies_from_db(raw_vac_db, tag_cfg.TAGS)
    # Save processed vacancies to statistics database.
    print(cfg.STAT_DB)
    stat_db = dm.open_db(cfg.STAT_DB)
    gather_time_sec = util.get_time_by_filename(args.db_name)
    proc_stat = ProcessedStatistics(processed_vacancies, gather_time_sec)
    proc_stat.calculate_all()
    stat_db.add(proc_stat)
    stat_db.commit()

    # Compress db if needed
    if args.compress:
        util.compress_database(args.db_name)


if __name__ == '__main__':
    main()
