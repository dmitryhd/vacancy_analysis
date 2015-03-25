Vacancy analysis
================
Web crawler and data analizer with web interface. 
Currently used to gather information about programmer vacancies.

How to use it:

2. Download statistics info to vacancy database: **./bin/vacan.proc**
3. Run web interface: **./bin/vacan.web**
4. Open http://localhost:9999 in your favorite browser and see results.

# Changelog

### v0.4 - rc
Reprocessing added, some issues with duplicate entry, find bug in migration

1. Databases
    - [X] Migrated to one common db
    - [X] Automated migration
    - [ ] Compression of database
    - [ ] Create reprocess function 
2. Statistics
    - [ ] Added more language tags
    - [ ] Fix java vs javascript bug
3. Bugs:
    - [X] Database locks a lot
    - [X] Web test actually uses one database for ages, rewriting it
    - [ ] No test separation


### v0.5 - featured
==========

1. Rewrite site parser
2. Collect from sj.ru.
