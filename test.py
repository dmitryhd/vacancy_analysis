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


if __name__ == '__main__':
    unittest.main()
