#!/usr/bin/env python3

""" Web server in python + flask. """

import os
import sys
sys.path.append('..')
from flask import request, Flask, render_template, send_from_directory, jsonify

import web_config as cfg
import processor.data_model as dm
from processor.statistics import ProcessedStatistics
from common.utility import round_to_thousands, format_timestamp
import common.tag_config as tag_cfg


app = Flask('web_interface.web')
app.debug = True

class StatisticsDbInterface(object):
    def __init__(self):
        self.stat_db = dm.open_db(cfg.STAT_DB, 'r')

    def __get_statistics(self, date):
        """ Return Processed statistics from specific date. """
        return self.stat_db.query(ProcessedStatistics).filter_by(date=date).first()

    def get_dates(self):
        """ Return list of all dates in int format. """
        statistics = self.stat_db.query(ProcessedStatistics)
        dates = [statistic.date for statistic in statistics]
        dates.sort(reverse=True)
        return dates

    def get_timestamps_and_dates(self):
        """ Return list of all dates in [int, datetime] format. """
        return [[tstamp, format_timestamp(tstamp)] for tstamp in self.get_dates()]

    def get_vac_num(self, date):
        """ Get number of vacancies from statistics. """
        stat = self.__get_statistics(date)
        stat_cat_val = zip(tag_cfg.TAG_NAMES,
                           [stat.num_of_vacancies[cat] for cat in tag_cfg.TAG_NAMES])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        categories = [cat_val[0] for cat_val in stat_cat_val]
        values = [cat_val[1] for cat_val in stat_cat_val]
        return categories, values

    def get_vac_salary(self, date):
        """ Get mean min and max of vacancies from statistics. """
        stat = self.__get_statistics(date)
        stat_cat_val = zip(tag_cfg.TAG_NAMES,
                           [stat.mean_max_salary[cat] for cat in tag_cfg.TAG_NAMES],
                           [stat.mean_min_salary[cat] for cat in tag_cfg.TAG_NAMES])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        categories = [cat_val[0] for cat_val in stat_cat_val]
        mean_max_salary = [cat_val[1] for cat_val in stat_cat_val]
        mean_min_salary = [cat_val[2] for cat_val in stat_cat_val]
        return categories, mean_max_salary, mean_min_salary

    def get_max_salaries(self, date, tag_name):
        stat = self.__get_statistics(date)
        return stat.max_salaries[tag_name]


@app.route('/_get_dates')
def get_dates_json():
    """ Serve list of all dates int format. """
    stat_if = StatisticsDbInterface()
    return jsonify(dates=stat_if.get_dates())


@app.route('/_get_date_statistics')
def get_date_statistics_json():
    """ Get number of vacancies, mean_max and mean_min salary for overview. """
    date = request.args.get('date', 0, type=int)
    stat_interface = StatisticsDbInterface()
    vac_num_categories, vacancy_number = stat_interface.get_vac_num(date)
    sal_categories, mean_max_salary, mean_min_salary = stat_interface.get_vac_salary(date)
    return jsonify(vac_num_categories=vac_num_categories,
                   sal_categories=sal_categories,
                   vacancy_number=vacancy_number,
                   mean_max_salary=mean_max_salary,
                   mean_min_salary=mean_min_salary)


@app.route('/_get_tag_statistics')
def get_tag_statistics_json():
    """ Get history of vacancy mean salaries by dates. """
    tag_name = request.args.get('tag', "", type=str)
    statistics_db = dm.open_db(cfg.STAT_DB, 'r')
    statistics = statistics_db.query(ProcessedStatistics)
    mean_max_salary = []
    mean_min_salary = []
    for stat in statistics:
        max_salary = stat.mean_max_salary[tag_name]
        mean_max_salary.append([stat.date * 1000, max_salary])
        min_salary = stat.mean_min_salary[tag_name]
        mean_min_salary.append([stat.date * 1000, min_salary])
    return jsonify(max_salary_history=mean_max_salary,
                   min_salary_history=mean_min_salary)


@app.route('/_get_tag_histogram')
def get_tag_histogram_json():
    """ Creates histogram of maximum salary. """
    tag_name = request.args.get('tag', "", type=str)
    date = request.args.get('date', 0, type=int)
    max_salaries = StatisticsDbInterface().get_max_salaries(date, tag_name)
    bottom_max_salary = min(max_salaries)
    bin_size = (max(max_salaries) - bottom_max_salary) / cfg.NUMBER_OF_BINS
    counts = [0] * cfg.NUMBER_OF_BINS
    for sal in max_salaries:
        for bin_num in range(cfg.NUMBER_OF_BINS):
            bin_edge = bottom_max_salary + (bin_num + 1) * bin_size
            if sal < round_to_thousands(bin_edge):
                counts[bin_num] += 1
                break
    bins = []
    for bin_num in range(cfg.NUMBER_OF_BINS):
        bin_edge_bot = bottom_max_salary + (bin_num) * bin_size
        bin_edge_top = bottom_max_salary + (bin_num + 1) * bin_size
        bins.append('от {} до {}'.format(round_to_thousands(bin_edge_bot),
                                       round_to_thousands(bin_edge_top)))
    return jsonify(bins=bins, counts=counts)

@app.route('/')
def index():
    """ Show general statisics. """
    stat_if = StatisticsDbInterface()
    return render_template('gallery.html', dates=stat_if.get_timestamps_and_dates(),
                           tags=tag_cfg.TAG_NAMES)


@app.route('/tag/')
def tag_view():
    """ Show statistics on specific tag. """
    stat_if = StatisticsDbInterface()
    tag_name = request.args.get('tag', "python", type=str)
    return render_template('lang.html', dates=stat_if.get_timestamps_and_dates(),
                           tag_name=tag_name)


if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    app.run(host='0.0.0.0', port=cfg.PORT)
