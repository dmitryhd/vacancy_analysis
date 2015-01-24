#!/usr/bin/env python3

""" Contain entry representation of statistics entry.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, PickleType

from vacancy_analysis.processor.data_model import Base
import vacancy_analysis.processor.processor_config as cfg
import vacancy_analysis.common.tag_config as tag_cfg


class ProcessedStatistics(Base):
    """ Table entry for vacancy statistics for certain time. """
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    date = Column(Integer)
    num_of_vacancies = Column(PickleType)
    min_salaries = Column(PickleType)
    max_salaries = Column(PickleType)
    mean_min_salary = Column(PickleType)
    mean_max_salary = Column(PickleType)

    def __init__(self, proc_vac, _time='now'):
        self.proc_vac = proc_vac
        self.date = int(time.time()) if _time == 'now' else _time

    def calculate_num_of_vacancies(self, tags=tag_cfg.TAGS):
        """ Calculate statistics for number of vacancies. """
        self.num_of_vacancies = {tag.name: 0 for tag in tags}
        for pvac in self.proc_vac:
            for tag_name, tag_val in pvac.tags.items():
                self.num_of_vacancies[tag_name] += tag_val

    def calculate_min_max_salaries(self, tags=tag_cfg.TAGS):
        """ Calculate statistics for minimun and maximum salaries. """
        self.max_salaries = {}
        self.min_salaries = {}
        for tag in tags:
            self.max_salaries[tag.name] = [pvac.max_salary for pvac in
                                           self.proc_vac if pvac.max_salary and
                                           pvac.tags[tag.name] == True]
            self.min_salaries[tag.name] = [pvac.min_salary for pvac in
                                           self.proc_vac if pvac.min_salary and
                                           pvac.tags[tag.name] == True]

    def calculate_mean_min_max_salary(self, tags=tag_cfg.TAGS):
        """ Calculate statistics for minimum and maximum salaries. """
        def get_mean_salary(self, tags, salary_param_name):
            salary_by_tag = {tag.name: [0, 0] for tag in tags}  # [counter, salary]
            for pvac in self.proc_vac:
                if not pvac.__getattribute__(salary_param_name):
                    continue
                for tag_name, tag_val in pvac.tags.items():
                    if tag_val:
                        salary_by_tag[tag_name][0] += 1
                        salary_by_tag[tag_name][1] += pvac.__getattribute__(
                            salary_param_name)
            for tag_name in salary_by_tag.keys():
                cnt, sum_salary = salary_by_tag[tag_name]
                salary_by_tag[tag_name] = sum_salary / cnt if cnt else 0
            return salary_by_tag
            
        self.mean_max_salary = get_mean_salary(self, tags, 'max_salary') 
        self.mean_min_salary = get_mean_salary(self, tags, 'min_salary') 

    def calculate_all(self):
        """ Fill all fields of this class with values. """
        self.calculate_num_of_vacancies()
        self.calculate_min_max_salaries()
        self.calculate_mean_min_max_salary()

    def __repr__(self):
        return 'Statistics: {}, num_vac: {}'.format(self.date,
                                                    self.num_of_vacancies)

