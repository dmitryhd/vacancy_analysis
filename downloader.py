#!/usr/bin/python3
#-*- coding: utf-8 -*-

import unittest
import time, random
import bs4
from urllib.request import *

# @arg url - unicode string - Html page url
# @return unicode string - Html page content
def GetURL (url):
  """ Get HTML page by its URL """
  headers = { 'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17" }
  req = Request (url, None, headers)
  response = urlopen (req)
  return response.read ().decode('utf-8')


def GetAllWacancies (url, description, maxJumps = 3):
  """ get next page """
  res = ""
  page = " "
  i = 0
  while page:
    res += page
    url = "http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Programmirovanie-Razrabotka?orderBy=2&itemsOnPage=20&areaId=1&specializationId=1.221&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=100&page="
    page = GetURL (url + str (i))
    i += 1
    if (i > maxJumps):
      break
    waitTime = 0.2 + 0.05 * random.randrange (1, 7)
    time.sleep (waitTime)
  return res


class Vacancy (object):
  def __init__ (self, name = "", salary_min = 0):
    self.name = name
    self.salary_min = salary_min
    self.salary_max = 0
    self.salary_med = 0

  def __repr__(self):
    return "Vacancy {} {}".format(self.name, self.salary_min)

  def __eq__(self, other): 
    return self.__dict__ == other.__dict__


def GetVacanciesFromPage (page):
  #TODO: logging
  soup = bs4.BeautifulSoup (page)
  res = []
  for child in soup.find_all ('div', class_='searchresult__name'):
    name = child.string
    min_sal = 0
    for elem in child.next_elements:
      if isinstance (elem, bs4.element.Tag) and elem.name == 'div':
        if elem.has_key('class') and elem['class'] == ['b-vacancy-list-salary']:
          min_sal = elem.string
          allDigits = re.findall (r'(\d*)', min_sal, re.M)
          min_sal = "".join(allDigits)
          min_sal = int (min_sal)
          break
    #print (min_sal)
    #print (name)
    res.append(Vacancy(name, min_sal))
  return res


def DownloadCategorized ():
  vacancy_types = {
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Administrator-baz-dannyh?orderBy=2&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30&from=CLUSTER_AREA&text=&itemsOnPage=500&specializationId=1.420&professionalAreaId=1&areaId=1' :
    'database admin',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Analitik?orderBy=2&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30&from=CLUSTER_AREA&text=&itemsOnPage=500&specializationId=1.420&professionalAreaId=1&areaId=1' :
    'analitik'}
  for url, vac_name in vacancy_types.items():
    print (url, vac_name)


class TestDownloader (unittest.TestCase):
  # TODO: smart commenting/uncommenting 
#  def testMultiplePages (self):
#    page = GetAllWacancies ("http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom?orderBy=2&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30&from=CLUSTER_AREA&text=&itemsOnPage=20&professionalAreaId=1&areaId=1", "it")
  #with open("test.html", "w") as fd:
  #    fd.write(page)
  #  cnt = page.count ("<body")
  #  print (cnt)
  #  self.assertEqual (cnt > 1, True)

  def testGetVacancyParams (self):
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary"> от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address"> (Москва),</span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div> """
    vac = GetVacanciesFromPage (page)[0]
    expectedVac = Vacancy("Архитектор (Delphi, interbase)", 90000)
    print (expectedVac)
    print (vac)
    self.assertEqual (expectedVac, vac)
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary">от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address">(Москва), </span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div>
    <div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary">от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address">(Москва), </span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div> """
    vac = GetVacanciesFromPage (page)
    self.assertEqual (len(vac) == 2, True)
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/7648301" target="_blank">Руководитель отдела веб-разработок</a></span></div><div class="b-vacancy-list-salary">
             от 90&nbsp;000
             до 120&nbsp;000
             руб.
        </div><div class="searchresult__placetime"><a href="/employer/235922">Крик Дизайн</a> <span class="searchresult__address">
     (Москва),
    </span><span class="b-vacancy-list-date">29&nbsp;марта</span>&nbsp;
      </div></div>"
    """
    vac = GetVacanciesFromPage (page)
    for v in vac:
      print (v)


if __name__ == '__main__':
  #DownloadCategorized ()
  unittest.main ()
