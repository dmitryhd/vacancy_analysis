#!/usr/bin/env python3

""" This file contains main configuration of vacancy analysis.
    Tags.
"""

from vacancy import Tag

Tags = [Tag('c++', 'c++', 'cpp'),
        Tag('java'),
        Tag('perl'),
        Tag('python'),
        Tag('sap'),
        Tag('bash'),
        Tag('perl'),
        Tag('ruby'),
        Tag('javascript'),
        Tag('php'),
        Tag('1c', '1c', 'onec'),
        Tag('c#', 'c#', 'csharp'),
        # Databases...
        # Os...
        # Position...
       ]

BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
TEST_BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=10&no_magic=true&page=1'
MAXIM_NUMBER_OF_PAGES = 1000
LABEL='Зарплата программистов по Москве. Данные {} на {}'
CURRENT_SITE = 'hh.ru'

label_file_name = 'data/label.txt'
