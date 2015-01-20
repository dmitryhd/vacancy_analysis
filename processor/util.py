#!/usr/bin/env python3

import time
import re
import os

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
