#!/usr/bin/env python3

""" Unittest file for vacancy processor module. """

import os
import sys
import unittest
import json
import sqlalchemy

import vacan.common.utility as util
import vacan.common.processor_config as proc_cfg
import vacan.common.web_config as web_cfg
import vacan.processor.data_model as dm
import vacan.processor.statistics as stat
import vacan.processor.vacancy_processor as vp
import vacan.processor.site_parser as sp
import vacan.common.tag_config as tag_cfg
import vacan.web_interface.web as web


TEST_DATA_DIR = 'test_data/'
REF_TIME = 10000000
REF_NUMBER_OF_VACANCIES = {'c#': 0, 'php': 0, 'sap': 0, 'java': 1,
                           'c++': 3, 'ruby': 0, 'perl': 0, 'bash': 0,
                           'javascript': 0, '1c': 0, 'python': 1}
REF_MIN_SALARIES = {'bash': [], 'javascript': [],
                    'c#': [], 'php': [], 'perl': [], 
                    'ruby': [], 'c++': [10000, 11000, 9000], 'python': [15000], 
                    'java': [10000], 'sap': [], '1c': []}
REF_MAX_SALARIES = {'c#': [], 'java': [15000], 
                    'ruby': [], 'sap': [], 'perl': [], 
                    'python': [], 'bash': [], 
                    'javascript': [], 'c++': [15000, 16000, 14000], '1c': [], 
                    'php': []} 
REF_MEAN_MIN_SALARIES = {'python': 15000, 'sap': 0, 'ruby': 0, 'php': 0,
                         '1c': 0, 'perl': 0, 'c++': 10000,
                         'javascript': 0, 'bash': 0,
                         'java': 10000, 'c#': 0}
REF_MEAN_MAX_SALARIES = {'python': 0, 'sap': 0, 'ruby': 0, 'php': 0,
                         '1c': 0, 'perl': 0, 'c++': 15000,
                         'javascript': 0, 'bash': 0,
                         'java': 15000, 'c#': 0}


def create_fictive_database(db_name):
    raw_vac_session = dm.open_db(db_name, 'w')
    raw_vacs = [dm.RawVacancy('1', '<td class="l-content-colum-1 b-v-info-content">java c++ от 10 000 до 15 000 </td>'),
                dm.RawVacancy('2', '<td class="l-content-colum-1 b-v-info-content">c++ от 11 000 до 16 000 </td>'),
                dm.RawVacancy('3', '<td class="l-content-colum-1 b-v-info-content">c++ от 9 000 до 14 000 </td>'),
                dm.RawVacancy('4', '<td class="l-content-colum-1 b-v-info-content">python от 15 000 </td>')]
    raw_vac_session.add_all(raw_vacs)
    raw_vac_session.commit()
    proc_vacs = dm.process_vacancies_from_db(raw_vac_session, tag_cfg.TAGS)
    ref_proc_stat = stat.ProcessedStatistics(proc_vacs, _time=REF_TIME)
    ref_proc_stat.calculate_all()
    raw_vac_session.add(ref_proc_stat)
    raw_vac_session.commit()
    return raw_vac_session, ref_proc_stat


class DatabaseTestCase(unittest.TestCase):
    """ Abstract class for any test case, which is using database. """
    @classmethod
    def setUpClass(cls):
        """ Prepare db. """
        cls.vacancy_session = dm.open_db(proc_cfg.DB_NAME_TEST, 'w')

    @classmethod
    def tearDownClass(cls):
        cls.vacancy_session.close()


class TestBasicDataModel(DatabaseTestCase):
    """ Test basic datamodel for raw vacancy. """

    def test_raw_vacancy_serialization(self):
        """ Writing raw vacancy in db and load it. """
        vac_name = 'test_vac_name'
        vac_html = 'test_vac_html от чч'
        vac = dm.RawVacancy(vac_name, vac_html)
        self.vacancy_session.add(vac)
        self.vacancy_session.commit()
        loaded_vac = self.vacancy_session.query(dm.RawVacancy).first()
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

    @classmethod
    def setUpClass(cls):
        cls.raw_vac_session, cls.ref_proc_stat = create_fictive_database(proc_cfg.DB_NAME_TEST_RAW)

    @classmethod
    def tearDownClass(cls):
        cls.raw_vac_session.close()
        dm.delete_mysql_db(proc_cfg.DB_NAME_TEST_RAW)

    def test_serialization(self):
        """ Save statistics to db, then load it. """
        new_proc_stat = self.raw_vac_session.query(stat.ProcessedStatistics).first()
        self.assertEqual(new_proc_stat.num_of_vacancies, self.ref_proc_stat.num_of_vacancies)
        self.assertEqual(new_proc_stat.min_salaries, self.ref_proc_stat.min_salaries)
        self.assertEqual(new_proc_stat.max_salaries, self.ref_proc_stat.max_salaries)
        self.assertEqual(new_proc_stat.mean_min_salary, self.ref_proc_stat.mean_min_salary)
        self.assertEqual(new_proc_stat.mean_max_salary, self.ref_proc_stat.mean_max_salary)

    def test_num_of_vacancies(self):
        """ Process statistics for number of vacancies. """
        self.assertEqual(self.ref_proc_stat.num_of_vacancies,
                         REF_NUMBER_OF_VACANCIES)

    def test_min_max_salaries(self):
        """ Process statistics for min and max salaries. """
        self.assertEqual(self.ref_proc_stat.min_salaries,
                         REF_MIN_SALARIES)
        self.assertEqual(self.ref_proc_stat.max_salaries,
                         REF_MAX_SALARIES)

    def test_mean_min_max_salaries(self):
        """ Process statistics for mean salaries. """
        proc_vacs = dm.process_vacancies_from_db(self.raw_vac_session, tag_cfg.TAGS)
        self.assertEqual(self.ref_proc_stat.mean_min_salary,
                         REF_MEAN_MIN_SALARIES)
        self.assertEqual(self.ref_proc_stat.mean_max_salary,
                         REF_MEAN_MAX_SALARIES)

    def test_date(self):
        """ Check if right date is present in test database. """
        self.assertEqual(self.ref_proc_stat.date, REF_TIME)
        

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
        return sparser.get_all_vacancies(self.vacancy_session, self.MAX_VAC_NUM)
        
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

    def test_main(self):
        """ Call processor with argument
            See if any assert arises.
        """
        sys.argv = ['./vacancy_processor', '-n', '2', '-d', proc_cfg.DB_NAME_TEST]
        vp.main()


class TestMigration(unittest.TestCase):
    """ Testing migration from sqlite to mysql. """

    def test_migrate(self):
        """ Check that given tar gz sqlite database of raw vacancions we can 
            migrate it to given mysql database.
        """
        migrator = dm.Migrator()
        vacs = migrator.get_vacancies('test_data/')
        self.assertTrue(vacs)
        self.assertGreater(len(vacs), 30)

    def test_untar(self):
        migrator = dm.Migrator('test_data/compr_raw_vac_ex.db.tgz')
        fname = migrator.untar_file('test_data/compr_raw_vac_ex.db.tgz')
        self.assertEqual(fname, '/tmp/vac_1426497962.db')

    def test_get_raw_vacs(self):
        migrator = dm.Migrator()
        vacs = migrator.get_raw_vacs('test_data/compr_raw_vac_ex.db.tgz')
        self.assertTrue(vacs)
        self.assertGreater(len(vacs), 5)




class TestServer(unittest.TestCase):
    """ Basic test of main page view. """
    TEST_STAT_DB_DATE = 10000000 # this date must be in STAT_DB
    TEST_STAT_DB_PARAMS = {'sal_categories': 'c++',
                           'mean_max_salary': 15000.0,
                           'mean_min_salary': 10000.0}

    @classmethod
    def setUpClass(cls):
        """ Init test app """
        create_fictive_database(proc_cfg.DB_NAME_TEST_RAW_WEB)
        web.app.config['DB_URI'] = proc_cfg.DB_NAME_TEST_RAW_WEB
        cls.app = web.app.test_client()

    @classmethod
    def tearDownClass(cls):
        #dm.delete_mysql_db(proc_cfg.DB_NAME_TEST_RAW)
        pass


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
