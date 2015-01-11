#!/usr/bin/env python3

import os
import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import unittest
import json

import web
import config as cfg
import processor.data_model as dm

cfg.PRINT_PROGRESS = False
cfg.STAT_DB = '../exchange/test_stat.db'
TEST_STAT_DB_DATE = 1420961760 # this date must be in STAT_DB
TEST_STAT_DB_PARAMS = {'sal_categories': 'java',
                       'mean_max_salary': 150000.0,
                       'mean_min_salary': 70000.0,
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
        assert TEST_STAT_DB_DATE in dates, dates

    def test_get_date_statistics(self):
        """ Trying to ask server about number of vacancies. """
        json_data = self.get_json('/_get_date_statistics'
                                  '?date=' + str(TEST_STAT_DB_DATE))
        assert json_data['vacancy_number']
        for parameter_name, expected_value in TEST_STAT_DB_PARAMS.items():
            assert json_data[parameter_name][0] == expected_value, 'got: {} {}'.format(json_data[parameter_name][0], parameter_name)

    def test_tag_statistics(self):
        """ Trying to ask server about specific tag statistics. """
        tag_stat = self.get_json('/_get_tag_statistics?tag=java')
        assert tag_stat['max_salary_history']
        assert tag_stat['min_salary_history']

    def test_tag_histogram(self):
        """ Trying to ask server about specific tag histogram. """
        tag_stat = self.get_json('/_get_tag_histogram?tag=java'
                                 '&date=' + str(TEST_STAT_DB_DATE))
        assert tag_stat['bins']
        assert tag_stat['counts']


    def test_index(self):
        """ Check if all elements are in main page. """
        elements = ['vac_number_container',
                    'vac_salary_container', 'Данные:', 'Теги:']
        index_html = self.get_html('/')
        for element in elements:
            assert element in index_html, \
                'no {} in {}'.format(element, index_html)

    def test_tag(self):
        """ Check if all elements are in page with detailed tag statistics. """
        for tag in cfg.TAGS:
            elements = ['Lang: {}'.format(tag.title), 'vac_salary_hist_container',
                        'vac_salary_histogram']
            index_html = self.get_html('/tag/?tag={}'.format(tag.title))
            for element in elements:
                assert element in index_html, \
                    'no {} in {}'.format(element, index_html)


def main():
    """ Safely run test. """
    try:
        unittest.main(warnings='ignore')
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise

if __name__ == '__main__':
    main()
