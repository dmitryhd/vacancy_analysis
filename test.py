#!/usr/bin/env python3

""" Unittest file for vacancy. """

# pylint: disable=F0401, C0103, E1101, R0904

import unittest
import os
import sys
import json

import config as cfg
cfg.PRINT_PROGRESS = False
cfg.STAT_DB = 'data/test/test_stat.db'
import igallery
import data_model as dm
import vacancy_processor as vp
import site_parser as sp

TEST_VAC_FILES = ['data/test/test_vac01.html',
                  'data/test/test_vac02.html',
                  'data/test/test_vac03.html',
                  'data/test/test_vac04.html',
                 ]

class TestProcessor(unittest.TestCase):
    """ Compress and decompress cetrain file. """
    @classmethod
    def tearDownClass(cls):
        os.remove('data/testfn.txt')

    @staticmethod
    def test_compress_decompress():
        """ Compress file, then decompress. """
        test_fn = 'data/testfn.txt'
        initial_text = 'abcdefg'
        with open(test_fn, 'w') as test_fd:
            test_fd.write(initial_text)
            test_fd.close()
        assert os.path.isfile(test_fn)
        with open(test_fn) as test_fd:
            assert test_fd.read() == initial_text
        vp.compress_database(test_fn)
        assert not os.path.isfile(test_fn)
        assert os.path.isfile(test_fn + '.tgz')
        vp.uncompress_database(test_fn + '.tgz')
        assert not os.path.isfile(test_fn + '.tgz')
        assert os.path.isfile(test_fn)
        with open(test_fn) as test_fd:
            assert test_fd.read() == initial_text

    @staticmethod
    def test_main():
        raw_vac_file = 'data/test/vac_1416631701.db'
        sys.argv = ['./vacancy_processor', '-p', '-d', raw_vac_file]
        vp.main()


class TestProcessedStatistics(unittest.TestCase):
    """ Save some processed data. """
    TEST_STAT_DB = 'data/test/test_stat_new.db'
    TEST_INFO_DB = 'data/test/test_stat_info.db'
    MAX_VAC = 10

    def tearDown(self):
        try:
            os.remove(self.TEST_STAT_DB)
        except FileNotFoundError:
            pass

    def test_save_some_statistics(self):
        """ Create processed statistics entry from example database. """
        statistics_db = dm.open_db(self.TEST_STAT_DB, 'w')
        raw_vacancies_db = dm.open_db(self.TEST_INFO_DB, 'r')
        proc_vacs = dm.process_vacancies_from_db(raw_vacancies_db, cfg.TAGS)
        proc_stat = dm.ProcessedStatistics(proc_vacs[:self.MAX_VAC],
                                           _time='now')
        proc_stat.calculate_all()
        statistics_db.add(proc_stat)
        statistics_db.commit()
        query = statistics_db.query(dm.ProcessedStatistics)
        assert query
        for vac_stat in query:
            assert vac_stat.date
            assert vac_stat.get_tag_bins()
            assert vac_stat.get_mean_max_salary()
            assert vac_stat.get_mean_min_salary()
            assert vac_stat.get_proc_vac()
            assert len(vac_stat.get_proc_vac()) <= self.MAX_VAC


class DatabaseTestCase(unittest.TestCase):
    """ Test case abstract class for any test case, which is using database.
    """
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


class TestVacancy(DatabaseTestCase):
    """ Test database, vacancy and processor. """
    TEST_CSV_FN = 'data/test/test.csv'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        try:
            os.remove(cls.TEST_CSV_FN)
        except FileNotFoundError:
            pass

    def test_vacancy(self):
        """ Case for vacancy class. """
        vac = dm.Vacancy('aaa', 'sdfvsdf')
        self.session.add(vac)
        self.session.commit()
        query = self.session.query(dm.Vacancy)
        assert query

    @staticmethod
    def test_tag():
        """ Case for processed vacancy class. """
        test_tags = [cfg.TagRepr('c++', 'c++', 'cpp'),
                     cfg.TagRepr('java', 'java', 'java'),
                     cfg.TagRepr('python', 'python', 'python'),
                    ]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = dm.Vacancy('test vacancy', vacancy_text)
        proc_vac = dm.ProcessedVacancy(vac, test_tags)
        assert proc_vac.name == 'test vacancy'
        assert proc_vac.tags[test_tags[0].name]
        assert proc_vac.tags[test_tags[1].name]
        assert not proc_vac.tags[test_tags[2].name]

    def test_output_csv(self):
        """ Test output to csv, regresstion test. """
        parser = sp.site_parser_factory('hh.ru')
        for vac_file in TEST_VAC_FILES:
            vac = parser.get_vacancy('aaa', open(vac_file).read(), 'nolink')
            self.session.add(vac)
        self.session.commit()
        processed_vacancies = dm.process_vacancies_from_db(self.session,
                                                           cfg.TAGS)
        vp.output_csv(processed_vacancies, tags=cfg.TAGS,
                      csv_file_name=self.TEST_CSV_FN)
        reference_text = open('data/test/test_reference.csv').read()
        output = open(self.TEST_CSV_FN).read()
        assert output == reference_text


class TestSiteParser(DatabaseTestCase):
    """ Test different sites. """
    MAX_VAC_NUM = 2

    def test_site_parser_hh(self):
        """ Create two site parsers and call get_all_vacancies. """
        sparser = sp.site_parser_factory('hh.ru')
        vacs = sparser.get_all_vacancies(self.session, self.MAX_VAC_NUM)
        assert vacs
        assert len(vacs) == self.MAX_VAC_NUM

    @staticmethod
    def test_composite_vacancy():
        """ Read test vacancy from html and check if output is right. """
        parser = sp.site_parser_factory('sj.ru')
        test_input = ['data/test/test_vac_sj_01.html',
                     ]
        for file_name in test_input:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy(html=testfd.read())
                assert test_vac.name and test_vac.name != 'cant parse'
                assert test_vac.html

    def test_site_parser_sj(self):
        """ Download data from superjob.ru """
        sparser = sp.site_parser_factory('sj.ru')
        vacs = sparser.get_all_vacancies(self.session, self.MAX_VAC_NUM)
        assert vacs

    def test_get_salary(self):
        """ Check, if we can parse hh vacancies """
        salaries = [(60000, 90000),
                    (None, 40000),
                    (70000, None),
                    (None, None),]
        result = zip(TEST_VAC_FILES, salaries)
        parser = sp.site_parser_factory('hh.ru')
        for file_name, (min_sal_exp, max_sal_exp) in result:
            with open(file_name) as testfd:
                test_vac = parser.get_vacancy('test_vac_name',
                                              testfd.read(),
                                              'nolink')
                pvac = vp.ProcessedVacancy(test_vac, [])
                assert pvac.min_salary == min_sal_exp, \
                        'Got salary: {}'.format(pvac.min_salary)
                assert pvac.max_salary == max_sal_exp, \
                        'Got salary: {}'.format(pvac.max_salary)


class TestServer(unittest.TestCase):
    """ Basic test of main page view. """
    def setUp(self):
        """ Init test app """
        self.app = igallery.app.test_client()
        igallery.stat_db = 'data/test/test_stat.db'
        self.stat_url = '/_get_statistics'
        self.query = self.stat_url + '?plot=/plots/plot_hh.ru_1417003723.png'

    def get_html(self, url):
        """ Get utf8 string, containig html code of url. """
        return self.app.get(url).data.decode('utf8')  # TODO: trainwreck?

    def get_json(self, url):
        """ Get utf8 string, containig json code of url. """
        data_text = self.get_html(url)
        return json.loads(data_text)

    def test_index(self):
        """ Check if all elements are in main page. """
        elements = ['iGallery', '<img', 'vac_number_container',
                    'vac_salary_container']
        index_html = self.get_html('/')
        for element in elements:
            assert element in index_html, \
                'no {} in {}'.format(element, index_html)

    def test_get_vac_num(self):
        """ Trying to ask server about number of vacancies. """
        json_data = self.get_json(self.query + '&ask=vac_num')
        assert 'd_values' in json_data, json_data
        assert 'd_categories' in json_data, json_data

    def test_get_vac_salary(self):
        """ Trying to ask server about salary. """
        json_data = self.get_json(self.query + '&ask=vac_sal')
        assert json_data
        assert json_data['categories'][0] == 'sap'
        assert json_data['mean_max_salary'][0] == 150000.0
        assert json_data['mean_min_salary'][0] == 130000.0
        assert json_data['categories'][2] == 'python'
        assert json_data['mean_max_salary'][2] == 112500.0
        assert int(json_data['mean_min_salary'][2]) == 80227


def main():
    """ Safely run test. """
    try:
        unittest.main(warnings='ignore')
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise

if __name__ == '__main__':
    main()
