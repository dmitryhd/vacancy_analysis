Current
==========

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
    - [ ] for all dates and individual vacancies and for tag 
- [ ] massive refactoring
    - [ ] delete old code in R
    - [ ] delete old code for statistics
    - [ ] documentation for information tables
    - [ ] rewrite interface for web
    - [ ] support of python docs
- [X] improve graphics
    
- [ ] autocomplete for markdown
# bugs
- [X] invalid html result in no html saved
- [ ] if we have no db - show message

### Classes
- [X] Feature
name
regexp
category
is_present

- [ ] ProcessedVacancy:
name
url
min max salary
features: {'name': True/False}
date begin
date closed

- [ ] VacancyProcessor
qualifier
salary_class
exp_class
process(raw_vacs): return ProcessedVacancy
_delete_duplicates(raw_vacs): return unique raw_vacs
_process_raw_vacancy(raw_vac): return processed_vac
_get_salary(text): return min_max_sal
_get_exp(text): return min_max_exp
_get_soup

- [X] Qualifier
generate by dict
contains set of features 
"analyze" by feature set sets features of procvac
get_salary
get_experience

- *DBManager*
db_name
dbengine
get_raw_vacs()


Database optimisation:
--------
### New struct
We have only 100mb free memory left, need to do smthing.

new database for vacancy must contain begin_date, cur_date, ended = False

when check vacancies:
    for vac in vacs:
        if vac.url in db.urls:
            db[url].ended = False
            db[url].cur_date = now

??
clear closed:
    db[url]. = now

### Compression
https://dev.mysql.com/doc/refman/5.6/en/innodb-compression-usage.html
or https://dev.mysql.com/doc/refman/5.1/en/encryption-functions.html

Future
===========
        * add recommender system
    - [ ] Web interface
        * filter by group of tags
        * nicer plots
        * top menu
        * about menu
        * statistics about collection
    - [ ] Rewrite site parser
    - [ ] Collect from sj.ru.
    - [ ] Plot uml diagramm
