#!/usr/bin/env python3

""" Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""
import bs4
import requests
from sys import stdout

from vacancy import Vacancy
from config import Sites

def site_parser_factory(site_name):
    print('site name', site_name)
    print('implementations:', ParserImpl)
    return ParserImpl[site_name](site_name)


class SiteParser():
    def __init__(self, name):
        self.name = name
        self.base_url = Sites[name]

    def get_vacancy(self, name, html, url):
        raise NotImplementedError

    def get_all_vacancies(self, maximum_vac, session):
        raise NotImplementedError

    def get_url(self, url):
        """ Get HTML page by its URL. """
        session = requests.Session()
        page = session.get(url).text
        # TODO: constant session
        return page



class SiteParserHH(SiteParser):
    def get_vacancy(self, name, html, url):
        """ Get base vacancy by name and html code of page. """
        new_html = ''
        soup = bs4.BeautifulSoup(html)
        # delete js
        [s.extract() for s in soup('script')]
        # delete style
        [s.extract() for s in soup('style')]
        res = soup.find('div', class_='b-important b-vacancy-info')
        if res:
            new_html += res.decode()
        res = soup.find('table', class_='l-content-2colums b-vacancy-container')
        if res:
            new_html += res.text
        #print(bs4.BeautifulSoup(new_html))
        return Vacancy(name, new_html, url=url, site='hh.ru')

    def get_vacancies_on_page(self, url, vacancies, session, maximum_vac):
        """ Download all vacancies from page and return link to next page. """
        page = self.get_url(url)
        soup = bs4.BeautifulSoup(page)
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
            link = soup.find_all('a', class_='b-pager__next-text')[1].attrs["href"]
        except IndexError:
            return None
        next_link = 'http://hh.ru' + link
        return next_link

    def get_all_vacancies(self, maximum_vac, session):
        vacancies = []
        next_link = self.base_url
        for i in range(maximum_vac):
            next_link = self.get_vacancies_on_page(next_link, vacancies, 
                                                   session, maximum_vac)
            if next_link == None:
                break
        return vacancies

ParserImpl = {'hh.ru': SiteParserHH}
