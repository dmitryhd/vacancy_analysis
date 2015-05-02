#!/usr/bin/env python3

""" Contain entry representation of statistics entry.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import json
import time
import sqlalchemy.types as types
from sqlalchemy.schema import Column
from sqlalchemy.ext import mutable

from vacan.processor.data_model import Base
import vacan.config as cfg
import vacan.skills as skills
import vacan.processor.data_model as dm
import vacan.utility as util


class JsonType(types.TypeDecorator):    
    impl = types.TEXT
    def process_bind_param(self, value, dialect):
        if value :
            return json.dumps(value)
        else:
            return {}
    def process_result_value(self, value, dialect):
        if value:
            return json.loads(value)
        else:
            return {}


mutable.MutableDict.associate_with(JsonType)


class ProcessedStatistics(Base):
    """ Table entry for vacancy statistics for certain time. """
    __tablename__ = cfg.DB_STATISTICS_TABLE
    id = Column(types.Integer, primary_key=True)
    date = Column(types.Integer)
    num_of_vacancies = Column(JsonType())
    min_salaries =     Column(JsonType())
    max_salaries =     Column(JsonType())
    mean_min_salary =  Column(JsonType())
    mean_max_salary =  Column(JsonType())

    def __init__(self, proc_vac, _time='now'):
        self.proc_vac = proc_vac
        self.date = int(time.time()) if _time == 'now' else _time

    def calculate_num_of_vacancies(self, tags=skills.SKILLS):
        """ Calculate statistics for number of vacancies. """
        num_of_vacancies = {tag.name: 0 for tag in tags}
        for pvac in self.proc_vac:
            for tag_name, tag_val in pvac.tags.items():
                num_of_vacancies[tag_name] += tag_val
        self.num_of_vacancies = num_of_vacancies


    def calculate_min_max_salaries(self, tags=skills.SKILLS):
        """ Calculate statistics for minimun and maximum salaries. """
        max_salaries = {}
        min_salaries = {}
        for tag in tags:
            max_salaries[tag.name] = [pvac.max_salary for pvac in
                                           self.proc_vac if pvac.max_salary and
                                           pvac.tags[tag.name] == True]
            min_salaries[tag.name] = [pvac.min_salary for pvac in
                                           self.proc_vac if pvac.min_salary and
                                           pvac.tags[tag.name] == True]
        self.max_salaries = max_salaries
        self.min_salaries = min_salaries

    def calculate_mean_min_max_salary(self, tags=skills.SKILLS):
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
        return 'Statistics: {}\n\tnum_vac: {}\n\tmin_sal: {}\n\tmax_sal: {}\n\tmean_min: {}'.format(self.date,
                                                    self.num_of_vacancies,
                                                    self.min_salaries,
                                                    self.max_salaries,
                                                    self.mean_min_salary)

