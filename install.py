#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import os

user = 'dimert'
path = os.path.dirname(os.path.abspath(__file__))
cron_line = '@daily dimert {}/vacancy_processor.py -t -c'.format(path)
print(cron_line)
with open('/etc/crontab', 'a+') as cron_fd:
    print(cron_line, file=cron_fd)


