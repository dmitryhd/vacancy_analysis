#!/usr/bin/env python3

""" This file contains main configuration of Data Analyzer.
"""

PORT = 80
NUMBER_OF_BINS = 20
WEB_DEBUG = True

MAXIM_NUMBER_OF_VACANCIES = 10000
DB_ENGINE = 'mysql'
#MYSQL_USER = 'vacan'
#MYSQL_PASSWD = 'vacan'
MYSQL_USER = 'root'
MYSQL_PASSWD = '111111'
DB_PREFIXES = {'sqlite': 'sqlite:/',
               'mysql': 'mysql+pymysql://{}:{}@localhost'.format(
                   MYSQL_USER, MYSQL_PASSWD)}

DB_PREFIX = DB_PREFIXES[DB_ENGINE]

DB_NAME = 'vacan_2015_05_09'
DB_VACANCIES_TABLE = 'vacancy'
DB_STATISTICS_TABLE = 'statistics'
DB_STATISTICS_LEN = 115000

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
