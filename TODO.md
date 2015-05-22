Current
==========

### v0.6rc
    - [ ] Tag system with support of
        * mutiple keywords for tag
        * regexp for tag
        * groups of tags
        * separate group for languages, professions, web tech, database tech, personal traits, mobile development
        * Fix java vs javascript bug

- [X] Vacancy
    - name
    - regexp
    - category
    - is_present

- [ ] ProcessedVacancy:
    - name
    - url
    - min max salary
    - features: {'name': True/False}
    - date begin
    - date closed

- [ ] Feature

- [X] Qualifier
    - generate by dict
    - contains set of features 
    - "analyze" by feature set sets features of procvac
    - get_salary
    - get_experience

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
