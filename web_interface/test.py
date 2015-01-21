#!/usr/bin/env python3

""" Web server testing. """

import os
import sys
import unittest
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append('..')

import web
import processor.data_model as dm
import web_config as cfg
import common.tag_config as tag_cfg

cfg.PRINT_PROGRESS = False
cfg.STAT_DB = '../common/test_stat.db'
TEST_STAT_DB_DATE = 1421741081 # this date must be in STAT_DB
TEST_STAT_DB_PARAMS = {'sal_categories': 'c#',
                       'mean_max_salary': 120000.0,
                       'mean_min_salary': 100000.0,
                      }

class TestServer(unittest.TestCase):
    """ Basic test of main page view. """

    def setUp(self):
        """ Init test app """
        self.app = web.app.test_client()
        web.stat_db = cfg.STAT_DB
        self.stat_url = '/_get_statistics'
        self.query = self.stat_url + '?plot=' + str(TEST_STAT_DB_DATE)

    def get_html(self, url):
        """ Get utf8 string, containig html code of url. """
        return self.app.get(url).data.decode('utf8')  # TODO: trainwreck?

    def get_json(self, url):
        """ Get utf8 string, containig json code of url. """
        data_text = self.get_html(url)
        return json.loads(data_text)

    def test_get_dates(self):
        """ Trying to ask server about entries available in database. """
        dates = self.get_json('/_get_dates')['dates']
        self.assertTrue(TEST_STAT_DB_DATE in dates)

    def test_get_date_statistics(self):
        """ Trying to ask server about number of vacancies. """
        json_data = self.get_json('/_get_date_statistics'
                                  '?date=' + str(TEST_STAT_DB_DATE))
        self.assertTrue(json_data['vacancy_number'])
        for parameter_name, expected_value in TEST_STAT_DB_PARAMS.items():
            self.assertEqual(json_data[parameter_name][0], expected_value)

    def test_tag_statistics(self):
        """ Trying to ask server about specific tag statistics. """
        tag_stat = self.get_json('/_get_tag_statistics?tag=java')
        self.assertTrue(tag_stat['max_salary_history'])
        self.assertTrue(tag_stat['min_salary_history'])

    def test_tag_histogram(self):
        """ Trying to ask server about specific tag histogram. """
        tag_stat = self.get_json('/_get_tag_histogram?tag=java'
                                 '&date=' + str(TEST_STAT_DB_DATE))
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
