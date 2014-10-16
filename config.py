#!/usr/bin/env python3

""" This file contains main configuration of vacancy analysis.
    Tags.
"""

Sites = {'hh.ru': 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'}

Tags = [('c++', 'c++', 'cpp'),
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
tag_name = 0
tag_text = 1
tag_title = 2

BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
TEST_BASE_URL = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=10&no_magic=true&page=1'
MAXIM_NUMBER_OF_PAGES = 1000
MAXIM_NUMBER_OF_VACANCIES = 10000
LABEL='Зарплата программистов по Москве. Данные {} на {}'
CURRENT_SITE = 'hh.ru'

label_file_name = 'data/label.txt'
