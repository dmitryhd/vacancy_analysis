#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import os

def main():
    """ Install to crontab. """
    user = 'dimert'
    path = os.path.dirname(os.path.abspath(__file__))
    cron_line = '@daily {} {}/vacancy_processor.py -t -c'.format(user, path)
    print(cron_line)
    #with open('/etc/crontab', 'a+') as cron_fd:
        #print(cron_line, file=cron_fd)

if __name__ == '__main__':
    main()

