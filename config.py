#!/usr/bin/env python3

""" This file contains main configuration of vacancy analysis.
    TAGS.
"""

SITE_URLS = {'hh.ru': 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1',
            'sj.ru': 'http://www.superjob.ru/vacancy/search/?sbmit=1&t[]=4&keywords[0][srws]=10&keywords[0][skwc]=and&keywords[0][keys]=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%B8%D1%81%D1%82&search_hesh=961543413088896&main=1'}

TAGS = [('c++', 'c++', 'cpp'),
        ('java', 'java', 'java'),
        ('perl', 'perl', 'perl'),
        ('python', 'python', 'python'),
        ('sap', 'sap', 'sap'),
        ('bash', 'bash', 'bash'),
        ('perl', 'perl', 'perl'),
        ('ruby', 'ruby', 'ruby'),
        ('javascript', 'javascript', 'javascript'),
        ('php', 'php', 'php'),
        ('1c', '1c', 'onec'),
        ('c#', 'c#', 'csharp'),
        # Databases...
        # Os...
        # Position...
       ]
TAG_NAME = 0
TAG_TEXT = 1
TAG_TITLE = 2

BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
TEST_BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=10&no_magic=true&page=1'
STAT_DB = 'data/stat.db'
MAXIM_NUMBER_OF_PAGES = 1000
MAXIM_NUMBER_OF_VACANCIES = 10000
LABEL = 'Зарплата программистов по Москве. Данные {} на {}'
CURRENT_SITE = 'hh.ru'

TITLE_FILENAME = 'data/tmp/title.txt'
PLOT_FILENAME_CONTAINER = 'data/tmp/plot_name.txt'
LABELS_FILENAME = 'data/tmp/pvac_labels.txt'
CSV_FILENAME = 'data/tmp/pvac.csv'

