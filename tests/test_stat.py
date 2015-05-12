#!/usr/bin/env python3

""" Unittest file for Statistics generation. """

import unittest

import tests
import vacan.processor.statistics as stat


class TestProcessedStatistics(unittest.TestCase):
    """ Save some processed data. """

    @classmethod
    def setUpClass(cls):
        cls.vac_db = tests.create_fictive_database()

    @classmethod
    def tearDownClass(cls):
        cls.vac_db.drop_database()

    def setUp(self):
        self.session = self.vac_db.get_session()
        self.proc_stat = self.session.query(stat.ProcessedStatistics).first()

    def tearDown(self):
        self.session.close()

    def test_num_of_vacancies(self):
        """ ProcessedStatistics: number of vacancies. """
        for tagname in tests.REF_NUMBER_OF_VACANCIES:
            self.assertEqual(self.proc_stat.num_of_vacancies[tagname],
                             tests.REF_NUMBER_OF_VACANCIES[tagname])

    def test_min_max_salaries(self):
        """ ProcessedStatistics: min and max salaries. """
        for tagname in tests.REF_MAX_SALARIES:
            self.assertEqual(self.proc_stat.min_salaries[tagname],
                             tests.REF_MIN_SALARIES[tagname])
            self.assertEqual(self.proc_stat.max_salaries[tagname],
                             tests.REF_MAX_SALARIES[tagname])

    def test_mean_min_max_salaries(self):
        """ ProcessedStatistics: mean salaries. """
        for tagname in tests.REF_MEAN_MIN_SALARIES:
            self.assertEqual(self.proc_stat.mean_min_salary[tagname],
                             tests.REF_MEAN_MIN_SALARIES[tagname])
            self.assertEqual(self.proc_stat.mean_max_salary[tagname],
                             tests.REF_MEAN_MAX_SALARIES[tagname])

    def test_date(self):
        """ ProcessedStatistics: if right date is present in test database. """
        self.assertEqual(self.proc_stat.date, tests.REF_TIME)

