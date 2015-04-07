#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    save to database.
    run: ./vacancy_processor.py -t -c
    Also can process database data to csv file for futher analysis.
    run: ./vacancy_processor.py -p -d <db_name>

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""

import time
import argparse
import sys
import os
import logging

import vacan.common.utility as util
import vacan.common.tag_config as tag_cfg
import vacan.common.processor_config as cfg
import vacan.processor.site_parser as sp
import vacan.processor.data_model as dm
from vacan.processor.statistics import ProcessedStatistics
import vacan.processor.statistics as stat

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def parse_args():
    """ Process command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db_name", type=str,
                        default='',
                        help="database name")
    parser.add_argument("-c", "--compress",
                        help="do compression",
                        action="store_true")
    parser.add_argument("-p", "--process", help="run process on given db",
                        action="store_true")
    parser.add_argument("-n", "--num_vac", help="none",
                        default=cfg.MAXIM_NUMBER_OF_VACANCIES, type=int)
    args = parser.parse_args()
    if not args.db_name:
        args.db_name = cfg.DB_NAME
    return args


def main():
    """ Download vacancies from site then process them to statistics
        and plot.
    """
    args = parse_args()

    logging.info('Download data from hh.ru ...')
    sparser = sp.site_parser_factory('hh.ru')
    db_manager = dm.DatabaseManager(cfg.DB_NAME)
    logging.debug('Database initialized ...')
    db_session = db_manager.get_session()
    vacs = sparser.get_all_vacancies(db_session, args.num_vac)
    logging.info('Download vacancies ' + str(len(vacs)) + ' ...')
    proc_vacs = dm.process_vacancies(vacs, tag_cfg.TAGS)
    logging.debug('Vacancies processed.')
    proc_stat = stat.ProcessedStatistics(proc_vacs)
    proc_stat.calculate_all()
    db_session.add(proc_stat)
    logging.debug('Statistics done.')
    logging.info('Saved to database.')
    db_session.commit()
    logging.debug('Commit done.')
    db_session.close()
    

    

if __name__ == '__main__':
    main()
