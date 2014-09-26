#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import bs4
from urllib.request import *
import re

# @arg url - unicode string - Html page url
# @return unicode string - Html page content
def GetURL (url):
  """ Get HTML page by its URL """
  headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17" }
  req = Request(url, None, headers)
  response = urlopen (req)
  return response.read().decode('utf-8')


class Vacancy (object):
  """struct to hold vacancy"""
  def __init__ (self, name = "", salary_min = 0, salary_max = 0):
    self.name = name
    self.salary_min = salary_min
    self.salary_max = salary_max

  def __repr__(self):
    return "{}; {}; {}".format(self.name, self.salary_min, self.salary_max)

  def __eq__(self, other): 
    return self.__dict__ == other.__dict__


# @arg page - utf8 html page
# @return list of Vacancies
def GetVacanciesFromPage (page):
  """ parse html page to get all vacancies names and salaries on it """
  def StringToInt (string):
    """ help function to parse salary """
    if not string:
      return 0
    allDigits = re.findall (r'(\d*)', string, re.M)
    min_sal = "".join(allDigits)
    try:
      return int (min_sal)
    except:
      return 0
  soup = bs4.BeautifulSoup (page)
  res = []
  for child in soup.find_all ('div', class_='searchresult__name'):
    name = child.string
    min_sal = 0
    max_sal = 0
    # get min and max salary here (от  10x00 до 123000 руб) -> 1000 - 123000
    for elem in child.next_elements:
      if isinstance (elem, bs4.element.Tag) and elem.name == 'div':
        if elem.has_key('class') and elem['class'] == ['b-vacancy-list-salary']:
          min_sal = StringToInt (elem.string.partition('до')[0])
          max_sal = StringToInt (elem.string.partition('до')[2])
          if (max_sal < min_sal):
            max_sal = min_sal
        break
    res.append (Vacancy (name, min_sal, max_sal))
  return res

# @arg dictionary {url, vac_name}
def DownloadCategorized (vacancy_types):
  """ download all vacancy types from dictionary by given url, parse them and save file,
  named vacancy_name.dat with lines of min and max salaries"""
  for url, vac_name in vacancy_types.items():
    print (vac_name)
    #page = GetAllWacancies (url, 1)
    page = GetURL (url)
    vac = GetVacanciesFromPage (page)
    with open (vac_name + ".dat", "w") as fd:
      fd.write ("min max\n")
      for v in vac:
        fd.write ("{} {}\n".format(v.salary_min, v.salary_max))




def main ():
  vacancy_types = {
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Administrator-baz-dannyh?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'database_admin',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Analitik?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'analitik',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Inzhener?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Inzhener',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Kompjuternaja-bezopasnost?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Kompjuternaja-bezopasnost',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Konsalting-Autsorsing?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Konsalting-Autsorsing',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Optimizacija-sajta-SEO?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Optimizacija-sajta-SEO',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Podderzhka-Helpdesk?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Podderzhka-Helpdesk',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Programmirovanie-Razrabotka?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'code',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Setevye-tehnologii?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Setevye-tehnologii',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Sistemnyj-administrator?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Sistemnyj-administrator',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Testirovanie?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'testirovanie',
    'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Tehnicheskij-pisatel?orderBy=2&itemsOnPage=2000&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' :
    'Tehnicheskij-pisatel'
    }
  DownloadCategorized (vacancy_types)





if __name__ == '__main__':
  main()
