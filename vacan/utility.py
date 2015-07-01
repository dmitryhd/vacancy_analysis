#!/usr/bin/env python3

""" Various independent functions"""

import time
import re
import argparse
import sys
import vacan
import vacan.config as cfg
from datetime import datetime


def date_to_int(date):
    """ Return int. """
    return int((date - datetime(1970, 1, 1)).total_seconds())


def int_to_date(timestamp):
    """ Return datetime. """
    return datetime.fromtimestamp(timestamp)


def round_to_thousands(num):
    """ Convert interger to kilos. """
    return int(round(num, -3))


def format_timestamp(timestamp):
    """ Get int to string time. """
    return datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')


def get_time_by_filename(fname):
    """ Get time in seconds from given string. If it doesn't contain any digist
        then - return current time.
    """
    seconds = re.search(r'(\d+)', fname)
    if not seconds:
        seconds = int(time.time())
    else:
        seconds = int(seconds.groups()[0])
    return seconds


def parse_args():
    """ Process command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action='store_true', 
                        help="print version and exit")
    parser.add_argument("-d", "--db_name", type=str,
                        default='',
                        help="database name")
    parser.add_argument("-n", "--num_vac",
                        help="number of offers to donwnload",
                        default=cfg.MAXIM_NUMBER_OF_VACANCIES, type=int)
    parser.add_argument("-f", "--folder",
                        help=("Folder to search for tgz archives."
                              "Only for migration"))
    args = parser.parse_args()
    if args.version:
        print('Version: ', vacan.__version__, ' release date:',
              vacan.__release_date__)
        sys.exit(0)
    if not args.db_name:
        args.db_name = cfg.DB_NAME
    return args


def create_histogram(data, bin_number):
    """ Create histogram data: return labels and counters. """
    bottom = min(data)
    #bin_size = (max(data) - bottom) / bin_number
    bin_size = 10000
    bin_number = int((max(data) - min(data)) / bin_size) + 1
    counts = [0] * bin_number
    for sal in data:
        for bin_num in range(bin_number):
            bin_edge = (bin_num + 1) * bin_size
            if sal < round_to_thousands(bin_edge):
                counts[bin_num] += 1
                break
    labels = []
    for bin_num in range(bin_number):
        bin_edge_bot = (bin_num) * bin_size
        bin_edge_top = (bin_num + 1) * bin_size
        labels.append('от {} до {}'.format(round_to_thousands(bin_edge_bot),
                                           round_to_thousands(bin_edge_top)))
    return labels, counts
