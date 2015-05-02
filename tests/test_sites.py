#!/usr/bin/env python3

""" Unittest file for testing of Site parser. """
import unittest
from tests import *

import vacan.processor.data_model as dm
import vacan.config as cfg
import vacan.processor.site_parser as sp
import vacan.processor.vacancy_processor


class TestSiteParser(unittest.TestCase):
    """ Test different sites. """
    MAX_VAC_NUM = 2
    TEST_VAC_FILES = [TEST_DATA_DIR + 'test_vac01.html',
                      TEST_DATA_DIR + 'test_vac02.html',
                      TEST_DATA_DIR + 'test_vac03.html',
                      TEST_DATA_DIR + 'test_vac04.html']
    
    def get_vacancies_from_site(self, site_name):
        """ SiteParser: Create valid site parser, download vacancies. """
        sparser = sp.site_parser_factory(site_name)
        db_man = dm.DBEngine(cfg.DB_NAME_TEST)
        return sparser.get_all_vacancies(db_man.get_session(),
                                         self.MAX_VAC_NUM)
        
    def test_site_parser_hh(self):
        """ SiteParser: Download data from hh.ru. """
        self.assertTrue(self.get_vacancies_from_site('hh.ru'))

    def test_site_parser_sj(self):
        """ SiteParser: Download data from superjob.ru """
        self.assertTrue(self.get_vacancies_from_site('sj.ru'))

    def test_composite_vacancy(self):
        """ SiteParser: Read test vacancy from html and check output. """
        # TODO: same for hh
        parser = sp.site_parser_factory('sj.ru')
        test_input = [TEST_DATA_DIR + 'test_vac_sj_01.html']
        for file_name in test_input:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy(html=testfd.read())
                self.assertTrue(test_vac.name)
                self.assertNotEqual(test_vac.name, 'cant parse')
                self.assertTrue(test_vac.html)

    def test_get_salary(self):
        """ SiteParser: Check, if we can get valid salaries from hh vac. """
        # TODO: same for sj
        salaries = [(60000, 90000), (None, 40000), (70000, None), (None, None)]
        result = zip(self.TEST_VAC_FILES, salaries)
        parser = sp.site_parser_factory('hh.ru')
        for file_name, (min_sal_exp, max_sal_exp) in result:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy('test_vac_name',
                                              testfd.read(),
                                              'nolink')
                pvac = vacan.processor.vacancy_processor.ProcessedVacancy(test_vac, [])
                self.assertEqual(pvac.min_salary, min_sal_exp)
                self.assertEqual(pvac.max_salary, max_sal_exp)

