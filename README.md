Vacancy analysis
================
Web crawler and data analizer with web interface.
Currently used to gather information about programmer vacancies.

How to use it:

1. Download statistics info to vacancy database: **./bin/vacan.download**
1. Run web interface: **./bin/vacan.monitor**
1. Open http://localhost:8080 in your favorite browser and see results.

Disclaimer
================

This is just fun site project for practicing some new programming techniques, do not expect too much.


Changelog
----------------

### v0.8 - release date: 01.03.2016
- 2 views:
    - [ ] for all dates and individual vacancies and for tag
- try out tornado

### v0.7 - release date: 01.02.2016
- [ ] working as a linux service
- [ ] make file support
- [ ] automatic deploy
- [ ] clean autonomous tests
- [ ] 100% test coverage
- [ ] web with bootstrap3
- [ ] delete old code in R
- [ ] delete old code for statistics
- [ ] documentation for information tables
- [ ] rewrite interface for web
- [ ] support of python docs


### v0.6rc
release date 2015.07.31 - fr
- [ ] Tag system with support of
    * mutiple keywords for tag
    * X regexp for tag
    * X groups of tags
    * X separate group for languages, professions, web tech, database tech, personal traits, mobile development
    * X Fix java vs javascript bug

- [X] Show only languages in web
- [X] Show rounded data
- [X] Get set of Processed vacancys by VacancyProcessor
- [X] Able to get subset of all vacancies with specific tags in notebook
- [X] Plot boxplots of subset in notebook
- [ ] 2 views:
    - [X] for individual date overall and for tag
    - [ ] for all dates and individual vacancies and for tag - next rel
- [X] improve graphics
- [X] autocomplete for markdown
# bugs
- [X] invalid html result in no html saved
- [ ] if we have no db - show message

Future
===========
add recommender system
- [ ] Web interface
    * filter by group of tags
    * nicer plots
    * top menu
    * about menu
    * statistics about collection
- Rewrite site parser
- Collect from sj.ru.
- Plot uml diagramm

Class diagram
================
![](https://raw.githubusercontent.com/dmitryhd/vacancy_analysis/analysis/project/development_doc/vacan_class_diagram.png)
