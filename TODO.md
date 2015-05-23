Current
==========

### v0.6rc
- [ ] Tag system with support of
    * mutiple keywords for tag
    * regexp for tag
    * groups of tags
    * separate group for languages, professions, web tech, database tech, personal traits, mobile development
    * Fix java vs javascript bug

- [ ] Get set of Processed vacancys by VacancyProcessor

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


* get vacancy skill by f

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
