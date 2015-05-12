#!/usr/bin/env python3

""" Core analysis module for scientific article.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""

import re
from collections import Counter

import vacan.processor.data_model as dm
import vacan.skills as skills
import vacan.processor.vacancy_processor


def analyze(dbmanager):
    """ Print to csv file with vacancies to stdout. """
    session = dbmanager.sessionmaker()
    raw_vacancies = session.query(dm.RawVacancy).all()
    processed_vacancies = []
    urls = set()
    print(form_csv_header())
    for raw_vacancy in raw_vacancies:
        # not adding duplicate vacancies, unique by url
        if raw_vacancy.url in urls:
            continue
        urls.add(raw_vacancy.url)
        proc_vac = vacan.processor.vacancy_processor.ProcessedVacancy(raw_vacancy, skills.SKILLS)
        print(form_csv_string(proc_vac))
        processed_vacancies.append(proc_vac)


def form_metric(tags):
    """ Return vector of vacancy. """
    vector = []
    for tag in skills.SKILLS:
        vector.append(int(tags[tag.name]))
    return vector


def form_csv_header():
    """ Return csv header. """
    header = '; '.join([tag.title for tag in skills.SKILLS])
    header += '; max_sal; min_sal; max_exp; min_exp; '
    return header


def form_csv_string(proc_vac):
    """ Return csv string from given vacancy. """
    csv = '; '.join(str(xi) for xi in form_metric(proc_vac.tags))
    csv += '; '
    csv += str(proc_vac.max_salary) + '; ' if proc_vac.max_salary else 'NA;'
    csv += str(proc_vac.min_salary) + '; ' if proc_vac.min_salary else 'NA;'
    csv += str(proc_vac.max_exp) + '; ' if proc_vac.max_exp else 'NA;'
    csv += str(proc_vac.min_exp) + '; ' if proc_vac.min_exp else 'NA;'
    return csv


def analyze_tags(dbmanager):
    """ Make frequency analysis of given database to get keyworkds.
        Return Counter object.
    """
    stops = ['and', 'the', 'work', 'skills', 'group',
             'with', 'for', 'business', 'development', 'you', 'end', 'will',
             'our', 'knowledge', 'are', 'company', 'good', 'requirements',
             'from', 'connect', 'studio', 'new', 'have', 'that',
             'working', 'ability', 'digital', 'etc', 'developer',
             'service', 'strong', 'software', 'dynamics', 'your',
             'time systems',
             'responsibilities', 'all', 'communication', 'code', 'clients',
             'application', 'word', 'client', 'high', 'market', 'professional',
             'within', 'technical', 'international', ]
    min_word_cnt = 5
    session = dbmanager.sessionmaker()
    raw_vacancies = session.query(dm.RawVacancy).all()
    urls = set()
    cnt = Counter()
    for raw_vacancy in raw_vacancies:
        if raw_vacancy.url in urls:
            continue
        urls.add(raw_vacancy.url)
        proc_vac = vacan.processor.vacancy_processor.ProcessedVacancy(raw_vacancy, skills.SKILLS)
        cur_bullets = proc_vac.get_all_bullets()
        cur_words = re.findall(r'([a-z]{3,})', cur_bullets) # only latin
        cnt.update(cur_words)
    for stop_word in stops:
        del cnt[stop_word]

    new_cnt = Counter()
    for word in cnt:
        if cnt[word] > min_word_cnt:
            new_cnt.update({word: cnt[word]})
    cnt = new_cnt
    return cnt

