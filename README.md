Vacancy analysis
================
Web crawler and data analizer with web interface. 
Currently used to gather information about programmer vacancies.

How to use it:

2. Download statistics info to vacancy database: **./bin/vacan_proc.py**
3. Run web interface: **./bin/vacan_web.py**
4. Open http://localhost:9999 in your favorite browser and see results.

Changelog
==========

v0.4 - rc
==========

1. Databases
    1. Migrated to one common db +
    2. Automated migration +
    3. Compression of database
    4. Create reprocess function 
2. Statistics
    1. Added more language tags
    2. Fix java vs javascript bug


v0.5 - rc
==========

1. Rewrite site parser
2. Collect from sj.ru.
