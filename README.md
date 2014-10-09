Vacancy analysis
================
Trying to get information about current state of job market in programming.
Use data from hh.ru to get vacancy information. 

How to use it:

1. Dowload info to vacancy sqlite database (data/vac.db): ./market_analysis.py 
2. Process vacancies with clusterization from database to csv file (data/pvac.csv): ./market_analysis.py -p
3. Analyse and visualize data from csv file by: Rscript plot.R. 
4. Plot saved in plots/vacancy_summary.png

Result plot example:
![Alt text](plots/vacancy_summary.png?raw=true "Result plot example")
