#!/usr/bin/python3
#-*- coding: utf-8 -*-

import unittest
from vacancy_statistics import *

class TestDownloader (unittest.TestCase):
  """just test suite"""
  def testSimpleVac (self):
    """ simple vacancy """
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary"> от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address"> (Москва),</span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div> """
    vac = GetVacanciesFromPage (page)[0]
    expectedVac = Vacancy("Архитектор (Delphi, interbase)", 90000, 90000)
    self.assertEqual (expectedVac, vac)

  def testMultipleVac (self):
    """ multiple vac """
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary">от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address">(Москва), </span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div>
    <div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6141931" target="_blank">Архитектор (Delphi, interbase)</a></span></div>
    <div class="b-vacancy-list-salary">от 90&nbsp;000 руб. </div><div class="searchresult__placetime"><a href="/employer/28439">ФГУП НИИ Почтовой связи</a> <span class="searchresult__address">(Москва), </span><span class="b-vacancy-list-date">30&nbsp;марта</span>&nbsp; </div></div> """
    vac = GetVacanciesFromPage (page)
    self.assertEqual (len(vac) == 2, True)

  def testMultipleVac (self):
    """ 1 vac, 2 sal """
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/7648301" target="_blank">Руководитель отдела веб-разработок</a></span></div><div class="b-vacancy-list-salary">
             от 90&nbsp;000
             до 120&nbsp;000
             руб.
        </div><div class="searchresult__placetime"><a href="/employer/235922">Крик Дизайн</a> <span class="searchresult__address">
     (Москва),
    </span><span class="b-vacancy-list-date">29&nbsp;марта</span>&nbsp;
      </div></div>"
    """
    vac = GetVacanciesFromPage (page)[0]
    expectedVac = Vacancy ("Руководитель отдела веб-разработок", 90000, 120000)
    self.assertEqual (expectedVac, vac)

  def testVacNoSalary (self):
    """ 1 vac, no sal """
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6892085" target="_blank">Java Developer</a></span></div><div class="b-vacancy-list-nosalary">
             з/п не указана
        </div><div class="searchresult__placetime"><a href="/employer/25">T-Systems CIS</a> <span class="searchresult__address">
     (Воронеж),
    </span><span class="b-vacancy-list-date">29&nbsp;марта</span>&nbsp;
      </div></div>"""
    vac = GetVacanciesFromPage (page)[0]
    expectedVac = Vacancy ("Java Developer", 0, 0)
    self.assertEqual (expectedVac, vac)

  def testVacOnlyMax (self):
    """ 1 vac, 1 sal """
    page = """<div class=""><div class="searchresult__name"><span class="b-marker"><a class="b-vacancy-list-link b-marker-link" href="http://hh.ru/vacancy/6892085" target="_blank">Java Developer</a></span></div>
        <div class="b-vacancy-list-salary">
             до 50 000
             руб.
        </div>    
             з/п не указана
        </div><div class="searchresult__placetime"><a href="/employer/25">T-Systems CIS</a> <span class="searchresult__address">
     (Воронеж),
    </span><span class="b-vacancy-list-date">29&nbsp;марта</span>&nbsp;
      </div></div>"""
    vac = GetVacanciesFromPage (page)[0]
    expectedVac = Vacancy ("Java Developer", 0, 50000)
    self.assertEqual (expectedVac, vac)

  # TODO: smart commenting/uncommenting 
  def testDownloader (self):
    """ test donwloader"""
    vacancy = {'http://hh.ru/catalog/Informacionnye-tehnologii-Internet-Telekom/Administrator-baz-dannyh?orderBy=2&itemsOnPage=20&areaId=1&from=CLUSTER_COMPENSATION&notWithoutSalary=true&specializationId=1.420&professionalAreaId=1&compensationCurrencyCode=RUR&noMagic=true&searchPeriod=30' : 'vac_test'};
    DownloadCategorized (vacancy)
    with open ("vac_test.dat", "r") as fd:
      res = fd.read()
      self.assertEqual (res.count('\n'), 21)


if __name__ == '__main__':
  unittest.main ()
