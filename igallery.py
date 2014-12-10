#!/usr/bin/env python3
# pylint: disable=invalid-name
""" Just a web server in python + flask. Shows content of folder images. """

import os
import glob
from flask import request, Flask, render_template, send_from_directory, jsonify

import config as cfg
import data_model as dm
import vacancy_processor as vp

stat_db = 'data/stat.db'
app = Flask(__name__)
app.debug = True

def run_server():
    """ Runs gallery. """
    app.run(host='0.0.0.0', port=cfg.PORT)


# --------------- AJAX ------------------
@app.route('/_get_dates')
def get_dates():
    """ Serve list of all dates int format. """
    statistics_db = dm.open_db(stat_db, 'r')
    statistics = statistics_db.query(dm.ProcessedStatistics)
    dates = [statistic.date for statistic in statistics]
    dates.sort(reverse=True)
    return jsonify(dates=dates)


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

@app.route('/_get_tag_statistics')
def get_tag_statistics():
    """ """
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
def get_tag_histogram():
    """ """
    tag_name = request.args.get('tag', "", type=str)
    # Get timestamp from plot to search database for statistics.
    date = request.args.get('date', 0, type=int)
    statistics_db = dm.open_db(stat_db, 'r')
    stat = statistics_db.query(dm.ProcessedStatistics).filter_by(date=date).first()
    pvacs = stat.get_proc_vac()
    max_salaries = [pvac.max_salary for pvac in pvacs if pvac.max_salary]
    bottom_max_salary = min(max_salaries)
    top_max_salary = max(max_salaries)
    NUMBER_OF_BINS = 20
    bin_size = (top_max_salary - bottom_max_salary) / NUMBER_OF_BINS
    counts = [0] * NUMBER_OF_BINS
    for sal in max_salaries:
        for bin_num in range(NUMBER_OF_BINS):
            bin_edge = bottom_max_salary + (bin_num + 1) * bin_size
            if sal < round_to_thousands(bin_edge):
                counts[bin_num] += 1
                break
    bins = []
    for bin_num in range(NUMBER_OF_BINS):
        bin_edge_bot = bottom_max_salary + (bin_num) * bin_size
        bin_edge_top = bottom_max_salary + (bin_num + 1) * bin_size
        bins.append('{} <-> {}'.format(round_to_thousands(bin_edge_bot),
                                         round_to_thousands(bin_edge_top)))
    return jsonify(bins=bins,
                   counts=counts)

def round_to_thousands(num):
    return int(round(num, -3))

@app.route('/_get_statistics')
def get_statistics():
    """ Serve statistics as json.
        Plot file name given by request.
    """
    plot_name = request.args.get('plot', "", type=str)
    # Get timestamp from plot to search database for statistics.
    timestamp = vp.get_time_by_filename(plot_name)
    statistics_db = dm.open_db(stat_db, 'r')
    req_type = request.args.get('ask', "", type=str)
    print('request type:', req_type)
    stat = statistics_db.query(
        dm.ProcessedStatistics).filter_by(date=timestamp).first()
    if req_type == 'vac_num':
        categories, values = get_vac_num(stat)
        return jsonify(d_categories=categories, d_values=values)
    elif req_type == 'vac_sal':
        categories, mean_max_salary, mean_min_salary = get_vac_salary(stat)
        return jsonify(categories=categories,
                       mean_max_salary=mean_max_salary,
                       mean_min_salary=mean_min_salary)


@app.route('/plots/<path:filename>')
def serve_plots(filename):
    """ Static function to serve png plots. """
    return send_from_directory('./plots/', filename)
# -------------- END AJAX ----------------


@app.route('/')
def index():
    """ Index view. """
    return render_template('gallery.html')

@app.route('/tag/<tag_name>')
def tag_view(tag_name):
    """ Index view. """
    return render_template('lang.html', tag_name=tag_name)

def main():
    """ Parse command line arguments. """
    run_server()


if __name__ == '__main__':
    main()
