#!/usr/bin/env python3

""" This file contains main configuration of vacancy analysis.
    TAGS.
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

TagRepr = namedtuple('Tag', ['name', 'text', 'title'])

TAGS = [TagRepr('c++', 'c++', 'cpp'),
        TagRepr('java', 'java', 'java'),
        TagRepr('perl', 'perl', 'perl'),
        TagRepr('python', 'python', 'python'),
        TagRepr('sap', 'sap', 'sap'),
        TagRepr('bash', 'bash', 'bash'),
        TagRepr('perl', 'perl', 'perl'),
        TagRepr('ruby', 'ruby', 'ruby'),
        TagRepr('javascript', 'javascript', 'javascript'),
        TagRepr('php', 'php', 'php'),
        TagRepr('1c', '1c', 'onec'),
        TagRepr('c#', 'c#', 'csharp'),
        # Databases...
        # Os...
        # Position...
       ]

MAXIM_NUMBER_OF_VACANCIES = 10000
LABEL = 'Зарплата программистов по Москве. Данные {} на {}'
STAT_DB = 'data/stat.db'

TITLE_FILENAME = 'data/tmp/title.txt'
PLOT_FILENAME_CONTAINER = 'data/tmp/plot_name.txt'
LABELS_FILENAME = 'data/tmp/pvac_labels.txt'
CSV_FILENAME = 'data/tmp/pvac.csv'

PORT = 9999
PLOT_PATH = './plots/'
PRINT_PROGRESS = True

NUMBER_OF_BINS = 20
