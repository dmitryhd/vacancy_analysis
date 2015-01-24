#!/usr/bin/env python3

""" Unittest file for vacancy processor module. """

import os
import sys
import unittest
import json

import vacancy_analysis.common.utility as util
import vacancy_analysis.processor.processor_config as proc_cfg
import vacancy_analysis.web_interface.web_config as web_cfg

proc_cfg.PRINT_PROGRESS = False
TEST_DATA_DIR = 'test_data/'
TEST_STAT_DB_PROC = TEST_DATA_DIR + 'test_stat_proc.db'
proc_cfg.STAT_DB = TEST_STAT_DB_PROC

import vacancy_analysis.processor.data_model as dm
import vacancy_analysis.processor.statistics as stat
import vacancy_analysis.processor.vacancy_processor as vp
import vacancy_analysis.processor.site_parser as sp
import vacancy_analysis.common.tag_config as tag_cfg
import vacancy_analysis.web_interface.web as web


class DatabaseTestCase(unittest.TestCase):
    """ Abstract class for any test case, which is using database. """
    TEST_DB = TEST_DATA_DIR + 'test.db'

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
        test_tags = [tag_cfg.TagRepr('c++', 'c++', 'cpp'),
                     tag_cfg.TagRepr('java', 'java', 'java'),
                     tag_cfg.TagRepr('python', 'python', 'python')]
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
    TEST_STAT_DB = TEST_DATA_DIR + 'test_stat_new.db'
    TEST_INFO_DB = TEST_DATA_DIR + 'test_stat_info.db'
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
        proc_vacs = dm.process_vacancies_from_db(raw_vacancies_db, tag_cfg.TAGS)
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
    TEST_VAC_FILES = [TEST_DATA_DIR + 'test_vac01.html',
                      TEST_DATA_DIR + 'test_vac02.html',
                      TEST_DATA_DIR + 'test_vac03.html',
                      TEST_DATA_DIR + 'test_vac04.html']
    
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
        test_input = [TEST_DATA_DIR + 'test_vac_sj_01.html']
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
    COMPRESS_FILE = TEST_DATA_DIR + 'testfn.txt'
    RAW_VAC_FILE = TEST_DATA_DIR + 'vac_1416631701.db'

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.COMPRESS_FILE)
            os.remove(TEST_STAT_DB_PROC)
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

    def test_main(self):
        """ Call processor with arguments. See if any assert arises. """
        sys.argv = ['./vacancy_processor', '-p', '-d', self.RAW_VAC_FILE]
        vp.main()

    def test_main_compress(self):
        """ Call processor with arguments and compress.
            See if any assert arises.
        """
        sys.argv = ['./vacancy_processor', '-c', '-t', '-n', '2']
        vp.main()

    def test_get_time_by_fname(self):
        """ Check get time. """
        self.assertEqual(util.get_time_by_filename('xx_1234'), 1234)
        self.assertTrue(util.get_time_by_filename('xx_'))


class TestServer(unittest.TestCase):
    """ Basic test of main page view. """
    TEST_STAT_DB_DATE = 1422081628  # this date must be in STAT_DB
    TEST_STAT_DB_PARAMS = {'sal_categories': 'c#',
                           'mean_max_salary': 145000.0,
                           'mean_min_salary': 95000.0, }

    def setUp(self):
        """ Init test app """
        web.app.config['DB_URI'] = TEST_DATA_DIR + 'test_stat_web.db'

        self.app = web.app.test_client()

    def get_html(self, url):
        """ Get utf8 string, containig html code of url. """
        return self.app.get(url).data.decode('utf8')

    def get_json(self, url):
        """ Get utf8 string, containig json code of url. """
        data_text = self.get_html(url)
        return json.loads(data_text)

    def test_get_dates(self):
        """ Trying to ask server about entries available in database. """
        dates = self.get_json('/_get_dates')['dates']
        self.assertTrue(self.TEST_STAT_DB_DATE in dates)

    def test_get_date_statistics(self):
        """ Trying to ask server about number of vacancies. """
        json_data = self.get_json('/_get_date_statistics'
                                  '?date=' + str(self.TEST_STAT_DB_DATE))
        self.assertTrue(json_data['vacancy_number'])
        for parameter_name, expected_value in self.TEST_STAT_DB_PARAMS.items():
            self.assertEqual(json_data[parameter_name][0], expected_value)

    def test_tag_statistics(self):
        """ Trying to ask server about specific tag statistics. """
        tag_stat = self.get_json('/_get_tag_statistics?tag=java')
        self.assertTrue(tag_stat['max_salary_history'])
        self.assertTrue(tag_stat['min_salary_history'])

    def test_tag_histogram(self):
        """ Trying to ask server about specific tag histogram. """
        tag_stat = self.get_json('/_get_tag_histogram?tag=java'
                                 '&date=' + str(self.TEST_STAT_DB_DATE))
        self.assertTrue(tag_stat['bins'])
        self.assertTrue(tag_stat['counts'])

    def test_index(self):
        """ Check if all elements are in main page. """
        elements = ['vac_number_container',
                    'vac_salary_container', 'Данные:', 'Теги:']
        index_html = self.get_html('/')
        for element in elements:
            self.assertTrue(element in index_html)

    def test_tag(self):
        """ Check if all elements are in page with detailed tag statistics. """
        for tag in tag_cfg.TAGS:
            elements = ['Lang: {}'.format(tag.title), 'vac_salary_hist_container',
                        'vac_salary_histogram']
            index_html = self.get_html('/tag/?tag={}'.format(tag.title))
            for element in elements:
                self.assertTrue(element in index_html)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
