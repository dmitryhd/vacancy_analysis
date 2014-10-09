#!/usr/bin/env python3

import unittest
from market_analysis import *
import os
from config import *

class TestFunc(unittest.TestCase):
    test_db = 'data/test.db'
    test_vac_files = ['data/test_vac01.html',
                      'data/test_vac02.html',
                      'data/test_vac03.html',
                      'data/test_vac04.html',
                      ]
    test_csv_fn = 'data/test.csv'

    @classmethod
    def setUpClass(cls):
        cls.session = prepare_db(cls.test_db)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.test_db)
            os.remove(cls.test_csv_fn)
        except FileNotFoundError:
            pass

    def test_vacancy(self):
        vac = Vacancy('aaa', 'sdfvsdf')
        self.session.add(vac)
        self.session.commit()
        query = self.session.query(Vacancy)
        assert query

    def test_tag(self):
        """ Test tag mechanism and proc_vacancy. """
        test_tags = [Tag('c++', 'c++', 'cpp'),
                     Tag('java'),
                     Tag('python'),
                    ]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = Vacancy('test vacancy', vacancy_text)
        proc_vac = ProcessedVacancy(vac, test_tags)
        assert proc_vac.name == 'test vacancy'
        assert proc_vac.tags[test_tags[0].name]
        assert proc_vac.tags[test_tags[1].name]
        assert not proc_vac.tags[test_tags[2].name]

    def test_get_salary(self):
        salaries = [(60000, 90000),
                    (None, 40000),
                    (70000, None),
                    (None, None),]
        for filename, (min_sal_exp, max_sal_exp) in zip(self.test_vac_files,
                salaries):
            with open(filename) as testfd:
                test_vac = get_vacancy('test_vac_name', testfd.read())
                pvac = ProcessedVacancy(test_vac, [])
                assert pvac.min_salary == min_sal_exp, \
                        'Got salary: {}'.format(pvac.min_salary)
                assert pvac.max_salary == max_sal_exp, \
                        'Got salary: {}'.format(pvac.max_salary)

    def test_process_vac(self):
        vacancies = []
        next_link = get_vacancies_on_page(TEST_BASE_URL, vacancies, self.session)
        assert next_link
        assert vacancies

    def test_output_csv(self):
        for vac_file in self.test_vac_files:
            vac = get_vacancy('aaa', open(vac_file).read())
            self.session.add(vac)
        self.session.commit()
        output_csv(self.session, file_name=self.test_csv_fn)
        reference_text =  open('data/test_reference.csv').read()
        output = open(self.test_csv_fn).read()
        assert output == reference_text

if __name__ == '__main__':
    unittest.main(warnings='ignore')
