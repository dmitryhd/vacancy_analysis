#!/usr/bin/env python3

""" Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""
import bs4
import requests
from sys import stdout

from vacancy import Vacancy
from config import Sites, MAXIM_NUMBER_OF_VACANCIES

def site_parser_factory(site_name):
    """ Must return site parser proper implementation. """
    return ParserImpl[site_name](site_name)


class SiteParser():
    """ Base class for parser. """
    def __init__(self, name):
        self.name = name
        self.base_url = Sites[name]
        self.web_session = requests.Session()

    def get_vacancy(self, name, html, url):
        """ Must return Vacancy. """
        raise NotImplementedError

    def get_all_vacancies(self, session,  maximum_vac=MAXIM_NUMBER_OF_VACANCIES):
        """ Must return list of vacancies and save them to session. """
        raise NotImplementedError

    def get_url(self, url):
        """ Get HTML page by its URL. """
        return self.web_session.get(url).text

    @staticmethod
    def _sanitize_html(html):
        """ Return soup without javascript and styles. """
        soup = bs4.BeautifulSoup(html)
        # delete js
        tmp = [s.extract() for s in soup('script')]
        # delete style
        tmp = [s.extract() for s in soup('style')]
        return soup


class SiteParserHH(SiteParser):
    """ Implementation of Head hunter parser. """

    def get_vacancy(self, name, html, url):
        """ Get base vacancy by name and html code of page. """
        new_html = ''
        soup = SiteParser._sanitize_html(html)
        res = soup.find('div', class_='b-important b-vacancy-info')
        if res:
            new_html += res.decode()
        res = soup.find('table',
                        class_='l-content-2colums b-vacancy-container')
        if res:
            new_html += res.text
        return Vacancy(name, new_html, url=url, site='hh.ru')

    def get_vacancies_on_page(self, url, vacancies, session, maximum_vac):
        """ Download all vacancies from page and return link to next page. """
        page = self.get_url(url)
        soup = bs4.BeautifulSoup(page)
        print('')
        for vacancy in soup.find_all('div', class_='searchresult__name'):
            name = vacancy.string
            if name is not None:
                link = vacancy.find_all('a')[0].attrs["href"]
                vacancy_html = self.get_url(link)
                new_vacancy = self.get_vacancy(name, vacancy_html, link)
                vacancies.append(new_vacancy)
                session.add(new_vacancy)
                session.commit()
                if len(vacancies) >= maximum_vac:
                    return None
                stdout.write("\rdownloaded {} vacancy".format(new_vacancy.id))
                stdout.flush()
        try:
            link = soup.find_all('a',
                                 class_='b-pager__next-text')[1].attrs["href"]
        except IndexError:
            return None
        next_link = 'http://hh.ru' + link
        return next_link

    def get_all_vacancies(self, session,
                          maximum_vac=MAXIM_NUMBER_OF_VACANCIES):
        """ Must return list of Vacancies. """
        vacancies = []
        next_link = self.base_url
        for i in range(maximum_vac):
            next_link = self.get_vacancies_on_page(next_link, vacancies,
                                                   session, maximum_vac)
            if next_link == None:
                break
        return vacancies


ParserImpl = {'hh.ru': SiteParserHH}
