#!/usr/bin/env python3

""" Various independent functions"""

from datetime import datetime

def round_to_thousands(num):
    """ Convert interger to kilos. """
    return int(round(num, -3))


def format_timestamp(timestamp):
    """ Get int to string time. """
    return datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
