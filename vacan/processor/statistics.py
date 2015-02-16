#!/usr/bin/env python3

""" Contain entry representation of statistics entry.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

from sqlalchemy.schema import Column
import sqlalchemy.types as types

from vacan.processor.data_model import Base
import vacan.common.processor_config as cfg
import vacan.common.tag_config as tag_cfg



import json
import sqlalchemy
from sqlalchemy import String, Text
from sqlalchemy.ext.mutable import Mutable

class JSONEncodedObj(sqlalchemy.types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class MutationObj(Mutable):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, MutationDict):
            return MutationDict.coerce(key, value)
        if isinstance(value, list) and not isinstance(value, MutationList):
            return MutationList.coerce(key, value)
        return value

    @classmethod
    def _listen_on_attribute(cls, attribute, coerce, parent_cls):
        key = attribute.key
        if parent_cls is not attribute.class_:
            return

        # rely on "propagate" here
        parent_cls = attribute.class_

        def load(state, *args):
            val = state.dict.get(key, None)
            if coerce:
                val = cls.coerce(key, val)
                state.dict[key] = val
            if isinstance(val, cls):
                val._parents[state.obj()] = key

        def set(target, value, oldvalue, initiator):
            if not isinstance(value, cls):
                value = cls.coerce(key, value)
            if isinstance(value, cls):
                value._parents[target.obj()] = key
            if isinstance(oldvalue, cls):
                oldvalue._parents.pop(target.obj(), None)
            return value

        def pickle(state, state_dict):
            val = state.dict.get(key, None)
            if isinstance(val, cls):
                if 'ext.mutable.values' not in state_dict:
                    state_dict['ext.mutable.values'] = []
                state_dict['ext.mutable.values'].append(val)

        def unpickle(state, state_dict):
            if 'ext.mutable.values' in state_dict:
                for val in state_dict['ext.mutable.values']:
                    val._parents[state.obj()] = key

        sqlalchemy.event.listen(parent_cls, 'load', load, raw=True, propagate=True)
        sqlalchemy.event.listen(parent_cls, 'refresh', load, raw=True, propagate=True)
        sqlalchemy.event.listen(attribute, 'set', set, raw=True, retval=True, propagate=True)
        sqlalchemy.event.listen(parent_cls, 'pickle', pickle, raw=True, propagate=True)
        sqlalchemy.event.listen(parent_cls, 'unpickle', unpickle, raw=True, propagate=True)

class MutationDict(MutationObj, dict):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionary to MutationDict"""
        self = MutationDict((k,MutationObj.coerce(key,v)) for (k,v) in value.items())
        self._key = key
        return self

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, MutationObj.coerce(self._key, value))
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()

class MutationList(MutationObj, list):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain list to MutationList"""
        self = MutationList((MutationObj.coerce(key, v) for v in value))
        self._key = key
        return self

    def __setitem__(self, idx, value):
        list.__setitem__(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def __setslice__(self, start, stop, values):
        list.__setslice__(self, start, stop, (MutationObj.coerce(self._key, v) for v in values))
        self.changed()

    def __delitem__(self, idx):
        list.__delitem__(self, idx)
        self.changed()

    def __delslice__(self, start, stop):
        list.__delslice__(self, start, stop)
        self.changed()

    def append(self, value):
        list.append(self, MutationObj.coerce(self._key, value))
        self.changed()

    def insert(self, idx, value):
        list.insert(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def extend(self, values):
        list.extend(self, (MutationObj.coerce(self._key, v) for v in values))
        self.changed()

    def pop(self, *args, **kw):
        value = list.pop(self, *args, **kw)
        self.changed()
        return value

    def remove(self, value):
        list.remove(self, value)
        self.changed()

def JSONAlchemy(sqltype):
    """A type to encode/decode JSON on the fly

    sqltype is the string type for the underlying DB column.

    You can use it like:
    Column(JSONAlchemy(Text(600)))
    """
    class _JSONEncodedObj(JSONEncodedObj):
        impl = sqltype
    return MutationObj.as_mutable(_JSONEncodedObj)


class ProcessedStatistics(Base):
    """ Table entry for vacancy statistics for certain time. """
    __tablename__ = 'statistics'
    id = Column(types.Integer, primary_key=True)
    date = Column(types.Integer)
    num_of_vacancies = Column(JSONAlchemy(Text(600)))
    min_salaries = Column(JSONAlchemy(Text(600)))
    max_salaries = Column(JSONAlchemy(Text(600)))
    mean_min_salary = Column(JSONAlchemy(Text(600)))
    mean_max_salary = Column(JSONAlchemy(Text(600)))

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

