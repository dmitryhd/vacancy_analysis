#!/usr/bin/env python3

""" This file contains main configuration of Universal Vacany Analyzer.
"""

from collections import namedtuple

SITE_URLS = {'hh.ru': 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80'
                      '%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%8'
                      '2&specialization=1&specialization=8&specialization=12'
                      '&specialization=14&area=1&salary=&currency_code=RUR&o'
                      'nly_with_salary=true&experience=&employment=full&orde'
                      'r_by=relevance&search_period=&items_on_page=100&no_ma'
                      'gic=true&page=1',
             'sj.ru': 'http://www.superjob.ru/vacancy/search/?sbmit=1&t[]=4&'
                      'keywords[0][srws]=10&keywords[0][skwc]=and&keywords[0'
                      '][keys]=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0'
                      '%B8%D1%81%D1%82&search_hesh=961543413088896&main=1'}

MAXIM_NUMBER_OF_VACANCIES = 10000
SQLITE_STATISTICS_DB = '/opt/vacan/common/stat.db'
DB_MAX_STRING_LEN = 100
DB_ENGINE = 'mysql'

MYSQL_USER = 'vacan'
MYSQL_PASSWD = 'vacan'
DB_PREFIXES = {'sqlite': 'sqlite:///',
               'mysql': 'mysql+mysqlconnector://{}:{}@localhost/'.format(
                    MYSQL_USER, MYSQL_PASSWD)}

DB_PREFIX = DB_PREFIXES[DB_ENGINE]

DB_NAME = 'vacan'
DB_NAME_TEST = 'vacan_t'
DB_NAME_TEST_RAW = 'vacan_raw_t'
DB_NAME_TEST_RAW_WEB = 'vacan_raw_test_web'
DB_NAME_TEST_TMP = 'vacan_t_tmp'
DB_VACANCIES_TABLE = 'vacancy'
DB_STATISTICS_TABLE = 'statistics'
DB_STATISTICS_LEN = 115000
