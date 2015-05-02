#!/usr/bin/env python3

""" Main module to download html pages fro hh.ru, parse them and
    save to database.

    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""
import argparse
import logging
import re
import bs4

import vacan.skills as skills
import vacan.config as cfg
import vacan.processor.site_parser as sp
import vacan.processor.data_model as dm
import vacan.processor.statistics as stat
from vacan.processor.data_model import RawVacancy


logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def process_vacancies_from_db(session, tags):
    """ Get list of processed vacancies from database of raw vacancies."""
    return process_vacancies(list(session.query(RawVacancy)), tags)


def process_vacancies(raw_vacs, tags):
    """ Return list of processed vacancies from list of raw. """
    return [ProcessedVacancy(vac, tags) for vac in raw_vacs]


class ProcessedVacancy():
    """ Processed vacancy. Contains name, tags and salary."""
    def __init__(self, vacancy, tags):
        """ Generate processed vacancy from vacancy. """
        self.name = vacancy.name
        soup = bs4.BeautifulSoup(vacancy.html)
        self.soup = soup
        text = soup.get_text()
        self.min_salary, self.max_salary = self.get_salary(soup)
        self.min_exp, self.max_exp = self.get_exp(soup)
        text = text.lower()
        self.tags = {}
        for tag in tags:
            if tag.text in text:
                self.tags[tag.name] = True
            else:
                self.tags[tag.name] = False

    @staticmethod
    def get_salary(soup):
        """ Get min and max salary from vacancy. """
        # TODO: extract method
        # TODO: extract data
        res = soup.find('td', class_='l-content-colum-1 b-v-info-content')
        if not res is None:
            digits = re.search(r'от\s+(\d+)\s+(\d*)', res.text)
            if digits:
                min_salary = int(''.join(digits.groups()))
            else:
                min_salary = None
            digits = re.search(r'до\s+(\d+)\s+(\d*)', res.text)
            if digits:
                max_salary = int(''.join(digits.groups()))
            else:
                max_salary = None
            return min_salary, max_salary
        return None, None

    @staticmethod
    def get_exp(soup):
        """ Get exp. """
        res = soup.find('td', class_='l-content-colum-3 b-v-info-content')
        if not res is None:
            digits = re.search(r'(\d+).*(\d+)', res.text)
            if digits:
                return int(digits.groups()[0]), int(digits.groups()[1])
        return None, None

    def get_all_bullets(self):
        """ TODO """
        return self.soup.get_text().lower()

    def __repr__(self):
        out = '{} {} {}'.format(self.name, self.min_salary, self.max_salary)
        out += '\ntags:' + str(self.tags)
        return out


def parse_args():
    """ Process command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db_name", type=str,
                        default='',
                        help="database name")
    parser.add_argument("-c", "--compress",
                        help="do compression",
                        action="store_true")
    parser.add_argument("-p", "--process", help="run process on given db",
                        action="store_true")
    parser.add_argument("-n", "--num_vac", help="none",
                        default=cfg.MAXIM_NUMBER_OF_VACANCIES, type=int)
    args = parser.parse_args()
    if not args.db_name:
        args.db_name = cfg.DB_NAME
    return args


def main():
    """ Download vacancies from site then process them to statistics
        and plot.
    """
    args = parse_args()

    logging.info('Download data from hh.ru ...')
    sparser = sp.site_parser_factory('hh.ru')
    db_manager = dm.DBEngine(cfg.DB_NAME)
    logging.debug('Database initialized ...')
    db_session = db_manager.get_session()
    vacs = sparser.get_all_vacancies(db_session, args.num_vac)
    logging.info('Download vacancies ' + str(len(vacs)) + ' ...')
    proc_vacs = process_vacancies(vacs, skills.SKILLS)
    logging.debug('Vacancies processed.')
    proc_stat = stat.ProcessedStatistics(proc_vacs)
    proc_stat.calculate_all()
    db_session.add(proc_stat)
    logging.debug('Statistics done.')
    logging.info('Saved to database.')
    db_session.commit()
    logging.debug('Commit done.')
    db_session.close()


if __name__ == '__main__':
    main()
