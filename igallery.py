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

def get_mean_max_salary_for_tag(stat, tag):
    """ """
    max_salaries = stat.get_mean_max_salary()[tag]
    return categories, mean_max_salary, mean_min_salary

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
    plot_data = []
    for stat in statistics:
        max_salary = stat.get_mean_max_salary()[tag_name]
        plot_data.append([stat.date * 1000, max_salary])
    return jsonify(max_salary_history=plot_data)


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
