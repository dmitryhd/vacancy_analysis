#!/usr/bin/env python3

""" Unittest file for vacancy processor module. """

import unittest
import os
import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import util
import config as cfg
cfg.PRINT_PROGRESS = False
TEST_STAT_DB = 'data/test/test_stat.db'
cfg.STAT_DB = TEST_STAT_DB
import data_model as dm
import statistics as stat
import vacancy_processor as vp
import site_parser as sp


class DatabaseTestCase(unittest.TestCase):
    """ Abstract class for any test case, which is using database. """
    TEST_DB = 'data/test/test.db'

    @classmethod
    def setUpClass(cls):
        """ Prepare db. """
        cls.session = dm.open_db(cls.TEST_DB, 'w')

    @classmethod
    def tearDownClass(cls):
        """ Delete db and tmp files. """
        try:
            os.remove(cls.TEST_DB)
        except FileNotFoundError:
            pass


class TestBasicDataModel(DatabaseTestCase):
    """ Test basic datamodel for raw vacancy. """

    def test_raw_vacancy_serialization(self):
        """ Writing raw vacancy in db and load it. """
        vac_name = 'test_vac_name'
        vac_html = 'test_vac_html'
        vac = dm.RawVacancy(vac_name, vac_html)
        self.session.add(vac)
        self.session.commit()
        loaded_vac = self.session.query(dm.RawVacancy).first()
        self.assertEqual(loaded_vac.name, vac_name)
        self.assertEqual(loaded_vac.html, vac_html)
        self.assertEqual(str(loaded_vac), str(vac))

    def test_processed_vacancy_creation(self):
        """ Creating processed vacancy from raw vacancy. """
        test_tags = [cfg.TagRepr('c++', 'c++', 'cpp'),
                     cfg.TagRepr('java', 'java', 'java'),
                     cfg.TagRepr('python', 'python', 'python')]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = dm.RawVacancy('test vacancy', vacancy_text)
        proc_vac = dm.ProcessedVacancy(vac, test_tags)
        self.assertEqual(proc_vac.name, 'test vacancy')
        self.assertTrue(proc_vac.tags[test_tags[0].name])
        self.assertTrue(proc_vac.tags[test_tags[1].name])
        self.assertFalse(proc_vac.tags[test_tags[2].name])
        self.assertTrue('test vacancy' in str(proc_vac))


class TestProcessedStatistics(unittest.TestCase):
    """ Save some processed data. """
    TEST_STAT_DB = 'data/test/test_stat_new.db'
    TEST_INFO_DB = 'data/test/test_stat_info.db'
    MAX_VAC = 10
    REF_TIME = 1000000000
    REF_NUMBER_OF_VACANCIES = {'c#': 2, 'php': 2, 'sap': 0, 'java': 4,
                               'c++': 0, 'ruby': 1, 'perl': 0, 'bash': 1,
                               'javascript': 3, '1c': 0, 'python': 1}
    REF_MIN_SALARIES = {'bash': [100000], 'javascript': [40000, 55000],
                        'c#': [60000, 90000], 'php': [40000], 'perl': [], 
                        'ruby': [], 'c++': [], 'python': [], 
                        'java': [100000, 40000, 55000], 'sap': [], '1c': []}
    REF_MAX_SALARIES = {'c#': [95000, 90000], 'java': [70000, 3500], 
                        'ruby': [3500], 'sap': [], 'perl': [], 
                        'python': [3500], 'bash': [], 
                        'javascript': [70000, 3500], 'c++': [], '1c': [], 
                        'php': [70000, 3500]} 
    REF_MEAN_MIN_SALARIES = {'python': 0, 'sap': 0, 'ruby': 0, 'php': 40000.0,
                             '1c': 0, 'perl': 0, 'c++': 0,
                             'javascript': 47500.0, 'bash': 100000.0,
                             'java': 65000.0, 'c#': 75000.0}
    REF_MEAN_MAX_SALARIES = {'c#': 92500.0, 'python': 3500.0, '1c': 0,
                             'javascript': 36750.0, 'c++': 0, 'ruby': 3500.0,
                             'sap': 0, 'perl': 0, 'bash': 0, 'java': 36750.0,
                             'php': 36750.0}

    def setUp(self):
        self.ref_proc_stat = self.get_statistics()

    def tearDown(self):
        try:
            os.remove(self.TEST_STAT_DB)
        except FileNotFoundError:
            pass

    def get_statistics(self):
        """ Create processed statistics entry from example database. """
        raw_vacancies_db = dm.open_db(self.TEST_INFO_DB, 'r')
        proc_vacs = dm.process_vacancies_from_db(raw_vacancies_db, cfg.TAGS)
        ref_proc_stat = stat.ProcessedStatistics(proc_vacs[:self.MAX_VAC],
                                                 _time=self.REF_TIME)
        ref_proc_stat.calculate_all()
        return ref_proc_stat

    def test_serialization(self):
        """ Save statistics to db, then load it. """
        # Save statistics to db
        statistics_db = dm.open_db(self.TEST_STAT_DB, 'w')
        statistics_db.add(self.ref_proc_stat)
        statistics_db.commit()
        # Restore statistics from db
        new_proc_stat = statistics_db.query(stat.ProcessedStatistics).first()
        self.assertEqual(new_proc_stat, self.ref_proc_stat)
        self.assertEqual(str(new_proc_stat), str(self.ref_proc_stat))

    def test_num_of_vacancies(self):
        """ Process statistics for number of vacancies. """
        self.assertEqual(self.ref_proc_stat.num_of_vacancies,
                         self.REF_NUMBER_OF_VACANCIES)

    def test_min_max_salaries(self):
        """ Process statistics for min and max salaries. """
        self.assertEqual(self.ref_proc_stat.min_salaries,
                         self.REF_MIN_SALARIES)
        self.assertEqual(self.ref_proc_stat.max_salaries,
                         self.REF_MAX_SALARIES)

    def test_mean_min_max_salaries(self):
        """ Process statistics for mean salaries. """
        self.assertEqual(self.ref_proc_stat.mean_min_salary,
                         self.REF_MEAN_MIN_SALARIES)
        self.assertEqual(self.ref_proc_stat.mean_max_salary,
                         self.REF_MEAN_MAX_SALARIES)

    def test_date(self):
        self.assertEqual(self.ref_proc_stat.date, self.REF_TIME)

        

class TestSiteParser(DatabaseTestCase):
    """ Test different sites. """
    MAX_VAC_NUM = 2
    TEST_VAC_FILES = ['data/test/test_vac01.html', 'data/test/test_vac02.html',
                      'data/test/test_vac03.html', 'data/test/test_vac04.html']
    
    def get_vacancies_from_site(self, site_name):
        """ Create valid site parser, download vacancies and return them. """
        sparser = sp.site_parser_factory(site_name)
        return sparser.get_all_vacancies(self.session, self.MAX_VAC_NUM)
        
    def test_site_parser_hh(self):
        """  Download data from hh.ru. """
        self.assertTrue(self.get_vacancies_from_site('hh.ru'))

    def test_site_parser_sj(self):
        """ Download data from superjob.ru """
        self.assertTrue(self.get_vacancies_from_site('sj.ru'))

    def test_composite_vacancy(self):
        """ Read test vacancy from html and check if output is right. """
        # TODO: same for hh
        parser = sp.site_parser_factory('sj.ru')
        test_input = ['data/test/test_vac_sj_01.html']
        for file_name in test_input:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy(html=testfd.read())
                self.assertTrue(test_vac.name)
                self.assertNotEqual(test_vac.name, 'cant parse')
                self.assertTrue(test_vac.html)

    def test_get_salary(self):
        """ Check, if we can get valid salaries from hh vac. """
        # TODO: same for sj
        salaries = [(60000, 90000), (None, 40000), (70000, None), (None, None)]
        result = zip(self.TEST_VAC_FILES, salaries)
        parser = sp.site_parser_factory('hh.ru')
        for file_name, (min_sal_exp, max_sal_exp) in result:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy('test_vac_name',
                                              testfd.read(),
                                              'nolink')
                pvac = dm.ProcessedVacancy(test_vac, [])
                self.assertEqual(pvac.min_salary, min_sal_exp)
                self.assertEqual(pvac.max_salary, max_sal_exp)


class TestProcessor(unittest.TestCase):
    """ Call processor with arguments and test all utils functions. """
    COMPRESS_FILE = 'data/testfn.txt'

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.COMPRESS_FILE)
            os.remove(TEST_STAT_DB)
        except FileNotFoundError:
            pass

    def test_compress_decompress(self):
        """ Compress file, then decompress. """
        # Create original file
        initial_text = 'abcdefg'
        with open(self.COMPRESS_FILE, 'w') as test_fd:
            test_fd.write(initial_text)
        # Compress it
        util.compress_database(self.COMPRESS_FILE)
        self.assertFalse(os.path.isfile(self.COMPRESS_FILE))
        self.assertTrue(os.path.isfile(self.COMPRESS_FILE + '.tgz'))
        # Decompress it
        util.uncompress_database(self.COMPRESS_FILE + '.tgz')
        self.assertFalse(os.path.isfile(self.COMPRESS_FILE + '.tgz'))
        self.assertTrue(os.path.isfile(self.COMPRESS_FILE))
        with open(self.COMPRESS_FILE) as test_fd:
            self.assertEqual(test_fd.read(), initial_text)

    @staticmethod
    def test_main():
        """ Call processor with arguments. See if any assert arises. """
        raw_vac_file = 'data/test/vac_1416631701.db'
        sys.argv = ['./vacancy_processor', '-p', '-d', raw_vac_file]
        vp.main()

    def test_get_time_by_fname(self):
        """ Check get time. """
        self.assertEqual(util.get_time_by_filename('xx_1234'), 1234)
        self.assertTrue(util.get_time_by_filename('xx_'))


if __name__ == '__main__':
    unittest.main()
