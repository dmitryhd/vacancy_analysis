#!/usr/bin/env python3

""" Web server in python + flask. """

import os
from flask import request, Flask, render_template, jsonify, g

import vacan.common.web_config as cfg
from vacan.processor.data_model import open_db
from vacan.processor.statistics import ProcessedStatistics
from vacan.common.utility import format_timestamp, create_histogram
import vacan.common.tag_config as tag_cfg


app = Flask(__name__)
app.config['DB_URI'] = cfg.STAT_DB
#app.debug = True


class StatisticsDbInterface(object):
    def __init__(self, db_uri):
        print('created db interface:', db_uri)
        self.stat_db = open_db(db_uri, 'r')

    def get_statistics(self, date):
        """ Return Processed statistics from specific date. """
        query = self.stat_db.query(ProcessedStatistics)
        print('get statistics:', query.first())
        return query.filter_by(date=date).first()

    def get_all_statistics(self):
        """ Return all processed statistics from all dates. """
        return self.stat_db.query(ProcessedStatistics)

    def get_dates(self):
        """ Return list of all dates in int format. """
        dates = [statistic.date for statistic in self.get_all_statistics()]
        dates.sort(reverse=True)
        return dates

    def get_timestamps_and_dates(self):
        """ Return list of all dates in [int, datetime] format. """
        return [[tstamp, format_timestamp(tstamp)] for tstamp in self.get_dates()]

    def get_vac_num(self, date):
        """ Get number of vacancies from statistics.
            Return dict with keys: 'labels' and 'values'
        """
        stat = self.get_statistics(date)
        stat_cat_val = zip(tag_cfg.TAG_NAMES,
                           [stat.num_of_vacancies[cat] for cat in tag_cfg.TAG_NAMES])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        labels_values = {}
        labels_values['vac_num_categories'] = [cat_val[0] for cat_val in stat_cat_val]
        labels_values['vacancy_number'] = [cat_val[1] for cat_val in stat_cat_val]
        return labels_values

    def get_vac_salary(self, date):
        """ Get mean min and max of vacancies from statistics. """
        stat = self.get_statistics(date)
        stat_cat_val = zip(tag_cfg.TAG_NAMES,
                           [stat.mean_max_salary[cat] for cat in tag_cfg.TAG_NAMES],
                           [stat.mean_min_salary[cat] for cat in tag_cfg.TAG_NAMES])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        data = {}
        data['sal_categories'] = [cat_val[0] for cat_val in stat_cat_val]
        data['mean_max_salary'] = [cat_val[1] for cat_val in stat_cat_val]
        data['mean_min_salary'] = [cat_val[2] for cat_val in stat_cat_val]
        return data 

    def get_max_salaries(self, date, tag_name):
        stat = self.get_statistics(date)
        return stat.max_salaries[tag_name]

@app.before_request
def before_request():
    g.db = StatisticsDbInterface(app.config['DB_URI'])
    

@app.route('/_get_dates')
def get_dates_json():
    """ Serve list of all dates int format. """
    return jsonify(dates=g.db.get_dates())


@app.route('/_get_date_statistics')
def get_date_statistics_json():
    """ Get number of vacancies, mean_max and mean_min salary for overview. """
    date = request.args.get('date', 0, type=int)
    data = {}
    data.update(g.db.get_vac_num(date))
    data.update(g.db.get_vac_salary(date))
    return jsonify(**data)


@app.route('/_get_tag_statistics')
def get_tag_statistics_json():
    """ Get history of vacancy mean salaries by dates. """
    tag_name = request.args.get('tag', "", type=str)
    mean_max_salary = []
    mean_min_salary = []
    for stat in g.db.get_all_statistics():
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
    max_salaries = g.db.get_max_salaries(date, tag_name)
    labels, counts = create_histogram(max_salaries, cfg.NUMBER_OF_BINS)
    return jsonify(bins=labels, counts=counts)


@app.route('/')
def index():
    """ Show general statisics. """
    return render_template('gallery.html', dates=g.db.get_timestamps_and_dates(),
                           tags=tag_cfg.TAG_NAMES)


@app.route('/tag/')
def tag_view():
    """ Show statistics on specific tag. """
    tag_name = request.args.get('tag', "python", type=str)
    return render_template('lang.html', dates=g.db.get_timestamps_and_dates(),
                           tag_name=tag_name)


def start_server():
    app.run(host='0.0.0.0', port=cfg.PORT)

        
if __name__ == '__main__':
    start_server()
