Vacancy analysis
================
Web crawler and data analizer with web interface. 
Currently used to gather information about programmer vacancies.

How to use it:

1. Create data folders: **mkdir -p /opt/vacan/data; mkdir -p /opt/vacan/common;**
2. Download statistics info to vacancy database: **./vacan_proc -c**
3. Run web interface: **./vacan_web**
4. Open http://localhost:9999 in your favorite browser and see results.

TODO
==========

1. Replace picke with json.
2. Make one sql database for raw vacancies.
3. Make migration script from old database scheme.
4. Migrate to /run catalog.
5. Rewrite site parser
6. Collect from sj.ru.
