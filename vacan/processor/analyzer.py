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
    return [int(tags[tag]) for tag in sorted(tags.keys())]


def metric_to_str(metric):
    return ' '.join(str(xi) for xi in metric)


def analyze(dbmanager):
    session = dbmanager.sessionmaker()
    raw_vacancies = session.query(dm.RawVacancy).all()
    processed_vacancies = []
    for raw_vacancy in raw_vacancies:
        proc_vac = dm.ProcessedVacancy(raw_vacancy, tcnf.TAGS)
        out = ''
        out += metric_to_str(form_metric(proc_vac.tags))
        out += ' ' + str(proc_vac.max_salary)
        out += ' ' + str(proc_vac.min_salary)
        out += ' ' + proc_vac.name
        print(out)
        processed_vacancies.append(proc_vac)


