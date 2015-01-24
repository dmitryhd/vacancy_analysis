#!/usr/bin/env python3

""" Various independent functions"""

import time
import re
import os
from datetime import datetime


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


def compress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    os.system('tar czf {} {}'.format(db_name + '.tgz', db_name))
    os.remove(db_name)


def uncompress_database(db_name):
    """ Create bz archive and delete sqlite database file. """
    os.system('tar xzf {} '.format(db_name))
    os.remove(db_name)
    return db_name.replace('.tgz', '')


def create_histogram(data, bin_number):
    """ Create histogram data: return labels and counters. """
    bottom = min(data)
    bin_size = (max(data) - bottom) / bin_number
    counts = [0] * bin_number
    for sal in data:
        for bin_num in range(bin_number):
            bin_edge = bottom + (bin_num + 1) * bin_size
            if sal < round_to_thousands(bin_edge):
                counts[bin_num] += 1
                break
    labels = []
    for bin_num in range(bin_number):
        bin_edge_bot = bottom + (bin_num) * bin_size
        bin_edge_top = bottom + (bin_num + 1) * bin_size
        labels.append('от {} до {}'.format(round_to_thousands(bin_edge_bot),
                                           round_to_thousands(bin_edge_top)))
    return labels, counts
