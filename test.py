#!/usr/bin/env python3

import unittest
from market_analysis import *
import os

class TestFunc(unittest.TestCase):
    test_db = 'data/test.db'
    def setUp(self):
        self.session = prepare_db(self.test_db)

    def tearDown(self):
        os.remove(self.test_db)

    def test_vacancy(self):
        vac = Vacancy('aaa', 'sdfvsdf')
        self.session.add(vac)
        self.session.commit()
        query = self.session.query(Vacancy)
        assert query

    def test_tag(self):
        test_tags = [Tag('c++', 'c++', 'cpp'),
                     Tag('java'),
                     Tag('python'),
                    ]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = Vacancy('test vacancy', vacancy_text)
        proc_vac = set_tags_to_vacancy(vac, test_tags)
        assert proc_vac.name == 'test vacancy'
        assert proc_vac.tags[test_tags[0].name]
        assert proc_vac.tags[test_tags[1].name]
        assert not proc_vac.tags[test_tags[2].name]

    def test_get_salary(self):
        test_vac_files = ['data/test_vac01.html',
                          'data/test_vac02.html',
                          'data/test_vac03.html',
                          'data/test_vac04.html',
                          ]
        salaries = [(60000, 90000),
                    (None, 40000),
                    (70000, None),
                    (None, None),]
        for filename, (min_sal_exp, max_sal_exp) in zip(test_vac_files, salaries):
            with open(filename) as testfd:
                test_vac = get_vacancy('test_vac_name', testfd.read())
                min_salary, max_salary = get_salary(test_vac)
                assert min_salary == min_sal_exp, 'Got salary: {}'.format(min_salary)
                assert max_salary == max_sal_exp, 'Got salary: {}'.format(max_salary)

if __name__ == '__main__':
    unittest.main()
