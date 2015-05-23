#!/usr/bin/env python3

""" Text categories by skill. """

import re
import bs4


class Feature(object):
    """  """
    def __init__(self, name, category='', regexp=None):
        self.name = name
        self.regexp = regexp if regexp else r'(^|\s){}($|\s)'.format(name)
        self.category = category

    def is_present(self, text):
        return bool(re.search(self.regexp, text))
        

class Qualifier(object):
    """ """
    def __init__(self, feature_dict):
        """ Feature dict formed as follows: {'category': {'feature1': regexp}}
        """
        self.features = {}
        for category, features in feature_dict.items():
            for name, regexp in features.items():
                self.features[name] = Feature(name, category, regexp)

    def normalize(self, text):
        return text.lower()

    def analyze(self, text):
        norm_text = self.normalize(text)
        text_features = {}
        for feature in self.features.values():
            text_features[feature.name] = feature.is_present(norm_text)
        return text_features


class ProcessedVacancy(object):
    """ Processed element of data. """
    def __init__(self, name, url, min_sal, max_sal, min_exp, max_exp):
        self.name = name
        self.url = url
        self.min_sal = min_sal
        self.max_sal = max_sal
        self.min_exp = min_exp
        self.max_exp = max_exp
        self.features = {}


class VacancyProcessor(object):
    """ VacancyProcessor: process ProcessedVacancy from RawVacancy. """
    def __init__(self, qualifier):
        self.qualifier = qualifier
        self.salary_class = 'l-content-colum-1 b-v-info-content'
        self.exp_class = 'l-content-colum-3 b-v-info-content'
        
    def process(self, raw_vacs):
        """ From list of raw_vacs return list of ProcessedVacancies. """
        unique_raw_vacs = self._delete_duplicates(raw_vacs)
        return [self._process_raw_vacancy(raw_vac) for raw_vac
                in unique_raw_vacs]

    def _delete_duplicates(self, raw_vacs):
        """ Return list of vacancies with unique urls. """
        urls = set()
        unique_raw_vacs = []
        for raw_vac in raw_vacs:
            if raw_vac.url in urls:
                continue
            urls.add(raw_vac.url)
            unique_raw_vacs.append(raw_vac)
        return unique_raw_vacs

    def _process_raw_vacancy(self, raw_vac):
        """ Return ProcessedVacancy from RawVacancy. """
        min_sal, max_sal = self._get_min_max_sal(raw_vac.html)
        min_exp, max_exp = self._get_min_max_exp(raw_vac.html)
        proc_vac = ProcessedVacancy(raw_vac.name, raw_vac.url,
                                    min_sal, max_sal, min_exp, max_exp)
        proc_vac.features = self.qualifier.analyze(raw_vac.html)
        return proc_vac
    
    def _get_min_max_sal(self, text):
        """ Get min and max salary from vacancy. """
        soup = self._get_soup(text)
        res = soup.find('td', class_=self.salary_class)
        min_salary, max_salary = None, None
        if not res is None:
            digits = re.search(r'от\s+(\d+)\s+(\d*)', res.text)
            min_salary = int(''.join(digits.groups())) if digits else None
            digits = re.search(r'до\s+(\d+)\s+(\d*)', res.text)
            max_salary = int(''.join(digits.groups())) if digits else None
        return min_salary, max_salary

    def _get_min_max_exp(self, text):
        soup = self._get_soup(text)
        res = soup.find('td', class_=self.exp_class)
        min_exp, max_exp = None, None
        if not res is None:
            digits = re.search(r'(\d+).*(\d+)', res.text)
            min_exp = int(digits.groups()[0]) if digits else None
            max_exp = int(digits.groups()[1]) if digits else None
        return min_exp, max_exp 

    @staticmethod
    def _get_soup(text):
        return bs4.BeautifulSoup(text)
