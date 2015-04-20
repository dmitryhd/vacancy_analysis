#!/usr/bin/env python3

""" Core analysis module for scientific article.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""

""" Plan for version sa0.1 (science article)
    - [ ] setup tags
    - [ ] mark all vacancies with these tags
    - [ ] calculate metrics for every vacancy
    - [ ] make regression models Salary vs Metrics
"""

import vacan.processor.data_model as dm
import vacan.common.tag_config as tcnf


def form_metric(tags):
    vector = []
    for tag in tcnf.TAGS:
        vector.append(int(tags[tag.name]))
    return vector


def metric_to_str(metric):
    return ' '.join(str(xi) for xi in metric)


def form_csv_header():
    header = '; '.join([tag.title for tag in tcnf.TAGS])
    header += '; max_sal; min_sal; '
    return header
    

def form_csv_string(proc_vac):
    vector = form_metric(proc_vac.tags)
    csv = '; '.join(str(xi) for xi in form_metric(proc_vac.tags))
    csv += '; '
    csv += str(proc_vac.max_salary) + '; ' if proc_vac.max_salary else 'NA;'
    csv += str(proc_vac.min_salary) + '; ' if proc_vac.min_salary else 'NA;'
    return csv


def form_human_readable_string(proc_vac):
    out = '{} {:7} {:7} {}'.format(metric_to_str(form_metric(proc_vac.tags)),
    str(proc_vac.max_salary), 
    str(proc_vac.min_salary), 
    str(proc_vac.name))
    return out


def analyze(dbmanager):
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
        proc_vac = dm.ProcessedVacancy(raw_vacancy, tcnf.TAGS)
        print(form_csv_string(proc_vac))
        processed_vacancies.append(proc_vac)
    #print('total:', len(processed_vacancies), len(raw_vacancies))


