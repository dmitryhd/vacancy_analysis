#!/usr/bin/env python3
# pylint: disable=F0401, R0921

""" Here goes site specific implementation of get vacancies.
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""

import bs4
import requests
from sys import stdout

from data_model import RawVacancy
from config import SITE_URLS, MAXIM_NUMBER_OF_VACANCIES, PRINT_PROGRESS

def site_parser_factory(site_name):
    """ Must return site parser proper implementation. """
    return PARSER_IMPL[site_name](site_name)


class SiteParser():
    """ Base class for parser. """
    vacancy_body_tags = []
    def __init__(self, name):
        self.name = name
        self.base_url = SITE_URLS[name]
        self.web_session = requests.Session()

    def get_vacancy(self, name='', html='', url=''):
        """ Must return RawVacancy. """
        raise NotImplementedError

    def get_all_vacancies(self, session,
                          maximum_vac=MAXIM_NUMBER_OF_VACANCIES):
        """ Must return list of vacancies and save them to session. """
        raise NotImplementedError

    def get_url(self, url):
        """ Get HTML page by its URL. """
        return self.web_session.get(url).text

    @staticmethod
    def _sanitize_html(html):
        """ Return soup without javascript and styles. """
        soup = bs4.BeautifulSoup(html)
        for js_element in soup('script'):
            js_element.extract()
        for style_element in soup('style'):
            style_element.extract()
        return soup

    def _compose_vacancy(self, html):
        """ Return clean body of given vacancy, using body tags. """
        new_html = ''
        soup = SiteParser._sanitize_html(html)
        for tag_name, tag_class in self.vacancy_body_tags:
            res = soup.find(tag_name, class_=tag_class)
            if res:
                new_html += res.decode()
        return new_html


class SiteParserHH(SiteParser):
    """ Implementation of Head hunter parser. """
    VACANCY_LINK_TAG = 'search-result-item__head'

    def get_vacancy(self, name='', html='', url=''):
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
        return RawVacancy(name, new_html, url=url, site='hh.ru')

    def get_vacancies_on_page(self, url, vacancies, session, maximum_vac):
        """ Download all vacancies from page and return link to next page. """
        page = self.get_url(url)
        soup = bs4.BeautifulSoup(page)
        if PRINT_PROGRESS:
            print('\n')
        for vacancy in soup.find_all('div', class_=self.VACANCY_LINK_TAG):
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
                if PRINT_PROGRESS:
                    stdout.write("\rdownloaded {} vacancy".format(
                        new_vacancy.id))
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
        cnt = 0
        while cnt < maximum_vac:
            next_link = self.get_vacancies_on_page(next_link, vacancies,
                                                   session, maximum_vac)
            if next_link == None:
                break
            cnt += 1
        return vacancies


class SiteParserSJ(SiteParser):
    """ Implementation of Head hunter parser. """
    # RawVacancy tag->class, which contains main body.
    vacancy_body_tags = (('div', 'VacancyView_details'),
                         ('div', 'VacancyView_salary'),
                         ('div', 'VacancyView_location')
                        )
    vac_name_tags = ('h1', 'VacancyView_title h_color_gray_dk')

    def get_vacancy(self, name='', html='', url=''):
        """ Get base vacancy by name and html code of page. """
        if not html and url:
            html = self.get_url(url)
        elif not html:
            raise ValueError('should give html or url.')
        new_html = self._compose_vacancy(html)
        if not name:
            soup = bs4.BeautifulSoup(html)
            res = soup.find(self.vac_name_tags[0], self.vac_name_tags[1])
            if res:
                name = res.text
            else:
                name = 'cant parse'
        return RawVacancy(name, new_html, url=url, site='sj.ru')

    def get_vacancies_on_page(self, url, vacancies, session, maximum_vac):
        """ Download all vacancies from page and return link to next page. """
        page = self.get_url(url)
        soup = bs4.BeautifulSoup(page)
        if PRINT_PROGRESS:
            stdout.write('\n')
        for link_to_vac in soup.find_all('a', class_='vacancy-url'):
            link = link_to_vac.attrs["href"]
            vacancy_html = self.get_url(link)
            new_vacancy = self.get_vacancy(html=vacancy_html, url=link)
            vacancies.append(new_vacancy)
            session.add(new_vacancy)
            session.commit()
            if len(vacancies) >= maximum_vac:
                return None
            if PRINT_PROGRESS:
                stdout.write("\rdownloaded {} vacancy".format(new_vacancy.id))
                stdout.flush()
        try:
            next_link_candidates = soup.find_all(
                'a', class_='row_navigation pagination-link')
            for next_link_cand in next_link_candidates:
                if 'следуюящая' in next_link_cand.text:
                    return next_link_cand.attrs['href']
        except AttributeError:
            return None
        return None

    def get_all_vacancies(self, session,
                          maximum_vac=MAXIM_NUMBER_OF_VACANCIES):
        """ Must return list of Vacancies. """
        vacancies = []
        next_link = self.base_url
        cnt = 0
        while cnt < maximum_vac:
            next_link = self.get_vacancies_on_page(next_link, vacancies,
                                                   session, maximum_vac)
            if next_link == None:
                break
            cnt += 1
        return vacancies


PARSER_IMPL = {'hh.ru': SiteParserHH,
               'sj.ru': SiteParserSJ}
