#!/usr/bin/env python3

""" Unittest file for Web server. """

import unittest
import json

from tests import create_fictive_database
import vacan.web_interface.web as web
import vacan.skills as skills


class TestWeb(unittest.TestCase):
    """ Basic test of main page view. """
    TEST_STAT_DB_DATE = 10000000 # this date must be in STAT_DB
    TEST_STAT_DB_PARAMS = {'sal_categories': 'c++',
                           'mean_max_salary': 15000.0,
                           'mean_min_salary': 10000.0}

    @classmethod
    def setUpClass(cls):
        """ Init test app """
        cls.test_db = create_fictive_database()
        web.app.db_manager = cls.test_db
        cls.app = web.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.test_db.dispose()
        del cls.app
        cls.test_db.drop_database()

    def get_html(self, url):
        """ Get utf8 string, containig html code of url. """
        return self.app.get(url).data.decode('utf8')

    def get_json(self, url):
        """ Get utf8 string, containig json code of url. """
        data_text = self.get_html(url)
        return json.loads(data_text)

    def test_get_dates(self):
        """ Web: Trying to ask server about entries available in database. """
        dates = self.get_json('/_get_dates')['dates']
        self.assertTrue(self.TEST_STAT_DB_DATE in dates)

    def test_get_date_statistics(self):
        """ Web: Trying to ask server about number of vacancies. """
        json_data = self.get_json('/_get_date_statistics'
                                  '?date=' + str(self.TEST_STAT_DB_DATE))
        self.assertTrue(json_data['vacancy_number'])
        for parameter_name, expected_value in self.TEST_STAT_DB_PARAMS.items():
            self.assertEqual(json_data[parameter_name][0], expected_value)

    def test_tag_statistics(self):
        """ Web: Trying to ask server about specific tag statistics. """
        tag_stat = self.get_json('/_get_tag_statistics?tag=java')
        self.assertTrue(tag_stat['max_salary_history'])
        self.assertTrue(tag_stat['min_salary_history'])

    def test_tag_histogram(self):
        """ Web: Trying to ask server about specific tag histogram. """
        tag_stat = self.get_json('/_get_tag_histogram?tag=java'
                                 '&date=' + str(self.TEST_STAT_DB_DATE))
        self.assertTrue(tag_stat['bins'])
        self.assertTrue(tag_stat['counts'])

    def test_index(self):
        """ Web: Check if all elements are in main page. """
        elements = ['vac_number_container',
                    'vac_salary_container', 'Данные', 'Теги']
        index_html = self.get_html('/')
        for element in elements:
            self.assertTrue(element in index_html, element)

    def test_tag(self):
        """ Web: Check if all elements with detailed tag statistics. """
        for tag in skills.SKILLS:
            elements = ['Lang: {}'.format(tag.title),
                        'vac_salary_hist_container',
                        'vac_salary_histogram']
            index_html = self.get_html('/tag/?tag={}'.format(tag.title))
            for element in elements:
                self.assertTrue(element in index_html)


class TestREST(unittest.TestCase):
    """ Basic RESTful API. """
    TEST_STAT_DB_DATE = 10000000 # this date must be in STAT_DB
    TEST_STAT_DB_PARAMS = {'sal_categories': 'c++',
                           'mean_max_salary': 15000.0,
                           'mean_min_salary': 10000.0}
    @classmethod
    def setUpClass(cls):
        """ Init test app """
        cls.test_db = create_fictive_database()
        web.app.db_manager = cls.test_db
        cls.app = web.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.test_db.dispose()
        del cls.app
        cls.test_db.drop_database()

    def get_html(self, url):
        """ Get utf8 string, containig html code of url. """
        return self.app.get(url).data.decode('utf8')

    def get_json(self, url):
        """ Get utf8 string, containig json code of url. """
        data_text = self.get_html(url)
        return json.loads(data_text)

    def test_date_statistics(self):
        """ TestREST: date statistic11. """
        url = '/api/overall/stat/'
        self.assertTrue(self.get_json(url)['a'])
