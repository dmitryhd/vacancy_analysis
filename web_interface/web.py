#!/usr/bin/env python3
# pylint: disable=invalid-name
""" Just a web server in python + flask. Shows content of folder images. """

from flask import request, Flask, render_template, send_from_directory, jsonify

import os
import sys
sys.path.append('..')
import config as cfg
import processor.data_model as dm
from utility import round_to_thousands, format_timestamp


stat_db = cfg.STAT_DB
app = Flask('web_interface.web')
app.debug = True


def get_dates():
    """ Return list of all dates int format. """
    statistics_db = dm.open_db(stat_db, 'r')
    statistics = statistics_db.query(dm.ProcessedStatistics)
    dates = [statistic.date for statistic in statistics]
    dates.sort(reverse=True)
    return dates


@app.route('/_get_dates')
def get_dates_json():
    """ Serve list of all dates int format. """
    return jsonify(dates=get_dates())


def get_vac_num(stat):
    """ Get number of vacancies from statistics. """
    categories = [tag.name for tag in cfg.TAGS]
    stat_cat_val = zip(categories,
                       [stat.get_tag_bins()[cat] for cat in categories])
    stat_cat_val = list(stat_cat_val)
    stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
    categories = [cat_val[0] for cat_val in stat_cat_val]
    values = [cat_val[1] for cat_val in stat_cat_val]
    return categories, values


def get_vac_salary(stat):
    """ Get mean min and max of vacancies from statistics. """
    categories = [tag.name for tag in cfg.TAGS]
    stat_cat_val = zip(categories,
                       [stat.get_mean_max_salary()[cat] for cat in categories],
                       [stat.get_mean_min_salary()[cat] for cat in categories])
    stat_cat_val = list(stat_cat_val)
    stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
    categories = [cat_val[0] for cat_val in stat_cat_val]
    mean_max_salary = [cat_val[1] for cat_val in stat_cat_val]
    mean_min_salary = [cat_val[2] for cat_val in stat_cat_val]
    return categories, mean_max_salary, mean_min_salary


@app.route('/_get_date_statistics')
def get_date_statistics_json():
    """ Get number of vacancies, mean_max and mean_min salary for overview. """
    date = request.args.get('date', 0, type=int)
    statistics_db = dm.open_db(stat_db, 'r')
    print(stat_db)
    stat = statistics_db.query(
        dm.ProcessedStatistics).filter_by(date=date).first()
    vac_num_categories, vacancy_number = get_vac_num(stat)
    sal_categories, mean_max_salary, mean_min_salary = get_vac_salary(stat)
    return jsonify(vac_num_categories=vac_num_categories,
                   sal_categories=sal_categories,
                   vacancy_number=vacancy_number,
                   mean_max_salary=mean_max_salary,
                   mean_min_salary=mean_min_salary)


@app.route('/_get_tag_statistics')
def get_tag_statistics_json():
    """ Get history of vacancy mean salaries by dates. """
    tag_name = request.args.get('tag', "", type=str)
    statistics_db = dm.open_db(stat_db, 'r')
    statistics = statistics_db.query(dm.ProcessedStatistics)
    mean_max_salary = []
    mean_min_salary = []
    for stat in statistics:
        max_salary = stat.get_mean_max_salary()[tag_name]
        mean_max_salary.append([stat.date * 1000, max_salary])
        min_salary = stat.get_mean_min_salary()[tag_name]
        mean_min_salary.append([stat.date * 1000, min_salary])
    return jsonify(max_salary_history=mean_max_salary,
                   min_salary_history=mean_min_salary)


@app.route('/_get_tag_histogram')
def get_tag_histogram_json():
    """ Creates histogram of maximum salary. """
    statistics_db = dm.open_db(stat_db, 'r')
    date = request.args.get('date', 0, type=int)
    stat = statistics_db.query(dm.ProcessedStatistics).filter_by(
        date=date).first()
    pvacs = stat.get_proc_vac()
    tag_name = request.args.get('tag', "", type=str)
    max_salaries = [pvac.max_salary for pvac in pvacs
                    if pvac.max_salary and pvac.tags[tag_name] == True]
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
    return jsonify(bins=bins,
                   counts=counts)


@app.route('/plots/<path:filename>')
def serve_plots(filename):
    """ Static function to serve png plots. """
    return send_from_directory('./plots/', filename)


@app.route('/')
def index():
    """ Show general statisics. """
    dates = [[timestamp, format_timestamp(timestamp)] for timestamp
             in get_dates()]
    tags = [tag.name for tag in cfg.TAGS]
    return render_template('gallery.html', dates=dates, tags=tags)


@app.route('/tag/')
def tag_view():
    """ Show statistics on specific tag. """
    tag_name = request.args.get('tag', "python", type=str)
    dates = [[timestamp, format_timestamp(timestamp)] for timestamp
             in get_dates()]
    return render_template('lang.html', dates=dates, tag_name=tag_name)


def main():
    """ Runs gallery. """
    os.chdir(os.path.dirname(sys.argv[0]))
    app.run(host='0.0.0.0', port=cfg.PORT)


if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    app.run(host='0.0.0.0', port=cfg.PORT)
