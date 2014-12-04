#!/usr/bin/env python3

""" Unittest file for vacancy. """

# pylint: disable=F0401, C0103, E1101, R0904

import unittest
import os

import config as cfg
cfg.PRINT_PROGRESS = False
import data_model as dm
import vacancy_processor as vp
import site_parser as sp
from igallery import app


class TestCompression(unittest.TestCase):
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
        vp.uncompress_database(test_fn)
        assert not os.path.isfile(test_fn + '.tgz')
        assert os.path.isfile(test_fn)
        with open(test_fn) as test_fd:
            assert test_fd.read() == initial_text


class TestProcessedStatistics(unittest.TestCase):
    """ Save some processed data. """
    test_db = 'data/test/test_stat.db'
    test_info_db = 'data/test/test_stat_info.db'
    MAX_VAC = 10

    def test_save_some_statistics(self):
        """ Create processed statistics entry from example database. """
        statistics_db = dm.open_db(self.test_db, 'w')
        raw_vacancies_db = dm.open_db(self.test_info_db, 'r')
        proc_vacs = dm.process_vacancies_from_db(raw_vacancies_db, cfg.TAGS)
        proc_stat = dm.ProcessedStatistics(proc_vacs[:self.MAX_VAC],
                                           _time='now')
        proc_stat.calculate_tag_bins()
        statistics_db.add(proc_stat)
        statistics_db.commit()
        query = statistics_db.query(dm.ProcessedStatistics)
        assert query
        for vac_stat in query:
            assert vac_stat.get_proc_vac()
            assert len(vac_stat.get_proc_vac()) <= self.MAX_VAC
            assert vac_stat.date
            assert vac_stat.get_tag_bins()


class BaseT(unittest.TestCase):
    """ Test case for everything. """
    test_db = 'data/test/test.db'
    test_vac_files = ['data/test/test_vac01.html',
                      'data/test/test_vac02.html',
                      'data/test/test_vac03.html',
                      'data/test/test_vac04.html',
                     ]
    test_csv_fn = 'data/test/test.csv'
    MAX_VAC_NUM = 2

    @classmethod
    def setUpClass(cls):
        """ Prepare db. """
        cls.session = dm.open_db(cls.test_db, 'w')

    @classmethod
    def tearDownClass(cls):
        """ Delete db and tmp files. """
        try:
            os.remove(cls.test_db)
            os.remove(cls.test_csv_fn)
        except FileNotFoundError:
            pass

class TestVacancy(BaseT):
    """ Test database, vacancy and processor. """

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
        for vac_file in self.test_vac_files:
            vac = parser.get_vacancy('aaa', open(vac_file).read(), 'nolink')
            self.session.add(vac)
        self.session.commit()
        processed_vacancies = dm.process_vacancies_from_db(self.session,
                                                           cfg.TAGS)
        vp.output_csv(processed_vacancies, tags=cfg.TAGS,
                      csv_file_name=self.test_csv_fn)
        reference_text = open('data/test/test_reference.csv').read()
        output = open(self.test_csv_fn).read()
        assert output == reference_text


class TestSiteParser(BaseT):
    """ Test different sites. """

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
        result = zip(self.test_vac_files, salaries)
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
        self.app = app.test_client()

    def test_index(self):
        """ Check if images are in main page. """
        res = self.app.get('/')
        assert 'iGallery' in str(res.data), str(res.data)
        assert '<img' in str(res.data), str(res.data)

def main():
    """ Safely run test. """
    try:
        unittest.main(warnings='ignore')
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise

if __name__ == '__main__':
    main()
