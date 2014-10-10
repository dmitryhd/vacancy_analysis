#!/usr/bin/env python3

""" Unittest file for vacancy. """

import unittest
import os

import config as cfg
import site_parser as sp
import vacancy as va
import vacancy_processor as vp

class TestFunc(unittest.TestCase):
    """ Test case for everything. """
    test_db = 'data/test.db'
    test_vac_files = ['data/test_vac01.html',
                      'data/test_vac02.html',
                      'data/test_vac03.html',
                      'data/test_vac04.html',
                     ]
    test_csv_fn = 'data/test.csv'

    @classmethod
    def setUpClass(cls):
        """ Prepare db. """
        cls.session = vp.prepare_db(cls.test_db)

    @classmethod
    def tearDownClass(cls):
        """ Delete db and tmp files. """
        try:
            os.remove(cls.test_db)
            os.remove(cls.test_csv_fn)
        except FileNotFoundError:
            pass

    def test_vacancy(self):
        """ Case for vacancy class. """
        vac = va.Vacancy('aaa', 'sdfvsdf')
        self.session.add(vac)
        self.session.commit()
        query = self.session.query(va.Vacancy)
        assert query

    @staticmethod
    def test_tag():
        """ Case for processed vacancy class. """
        test_tags = [('c++', 'c++', 'cpp'),
                     ('java', 'java', 'java'),
                     ('python', 'python', 'python'),
                    ]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = va.Vacancy('test vacancy', vacancy_text)
        proc_vac = va.ProcessedVacancy(vac, test_tags)
        assert proc_vac.name == 'test vacancy'
        assert proc_vac.tags[test_tags[0][cfg.tag_name]]
        assert proc_vac.tags[test_tags[1][cfg.tag_name]]
        assert not proc_vac.tags[test_tags[2][cfg.tag_name]]

    def test_get_salary(self):
        """ Check, if we can parse hh vacancies """
        salaries = [(60000, 90000),
                    (None, 40000),
                    (70000, None),
                    (None, None),]
        result = zip(self.test_vac_files, salaries)
        for filename, (min_sal_exp, max_sal_exp) in result:
            with open(filename) as testfd:
                test_vac = vp.get_vacancy('test_vac_name',
                                          testfd.read(),
                                          'nolink')
                pvac = vp.ProcessedVacancy(test_vac, [])
                assert pvac.min_salary == min_sal_exp, \
                        'Got salary: {}'.format(pvac.min_salary)
                assert pvac.max_salary == max_sal_exp, \
                        'Got salary: {}'.format(pvac.max_salary)

    def test_process_vac(self):
        """ Need internet connection for this. """
        vacancies = []
        next_link = vp.get_vacancies_on_page(cfg.TEST_BASE_URL,
                                             vacancies,
                                             self.session)
        assert next_link
        assert vacancies

    def test_output_csv(self):
        """ Test output to csv, regresstion test. """
        for vac_file in self.test_vac_files:
            vac = vp.get_vacancy('aaa', open(vac_file).read(), 'nolink')
            self.session.add(vac)
        self.session.commit()
        vp.output_csv(self.session, file_name=self.test_csv_fn)
        reference_text = open('data/test_reference.csv').read()
        output = open(self.test_csv_fn).read()
        assert output == reference_text

    def test_various_site(self):
        """ Do we can access different sites? """
        hh_parser = sp.site_parser_factory('hh.ru')
        vac = hh_parser.get_vacancy('test_vac',
                                    open(self.test_vac_files[0]).read(),
                                    'someurl')
        assert vac
        vacancies = hh_parser.get_all_vacancies()
        assert vacancies



if __name__ == '__main__':
    try:
        unittest.main(warnings='ignore')
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise
