#!/usr/bin/env python3

""" Web server in python + flask. """

from flask import request, Flask, render_template, jsonify, g
from flask_restful import Resource, Api

import vacan.config as cfg
from vacan.processor.statistics import ProcessedStatistics
from vacan.utility import format_timestamp, create_histogram
import vacan.skills as skills
import  vacan.processor.data_model as data_model

app = Flask(__name__)
app.debug = cfg.WEB_DEBUG
app.db_manager = data_model.DBEngine(cfg.DB_NAME)
api = Api(app)

"""
'/api/overall/stat/': dates:list, vac_num, vac_salary,
'/api/overall/feature/<str:feature_name>': histograms
'/api/date/stat/<int:timestamp>': dates:list, vac_num, vac_salary,
'/api/date/feature/<str:feature_name>/<int:timestamp>/': histogram
"""

class Stat(Resource):
    def get(self):
        """ Return statistics for specific date. """
        return {'a': 'b'}

api.add_resource(Stat, '/api/overall/stat/')


class WebDbConnector(object):
    """ Interface used by web to database. """
    # TODO: refactor this
    def __init__(self, db_manager):
        self.stat_db = db_manager.get_session()

    def __del__(self):
        self.stat_db.close()

    def get_statistics(self, date):
        """ Return Processed statistics from specific date. """
        query = self.stat_db.query(ProcessedStatistics)
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
        name_list = skills.CATEGORIES['languages']
        print(name_list)
        stat_cat_val = zip(name_list,
                           [stat.num_of_vacancies[cat] for cat in name_list])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        labels_values = {}
        labels_values['vac_num_categories'] = [cat_val[0] for cat_val in stat_cat_val]
        labels_values['vacancy_number'] = [cat_val[1] for cat_val in stat_cat_val]
        return labels_values

    def get_vac_salary(self, date):
        """ Get mean min and max of vacancies from statistics. """
        stat = self.get_statistics(date)
        name_list = skills.CATEGORIES['languages']
        stat_cat_val = zip(name_list,
                           [stat.mean_max_salary[cat] for cat in name_list],
                           [stat.mean_min_salary[cat] for cat in name_list])
        stat_cat_val = list(stat_cat_val)
        stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
        data = {}
        data['sal_categories'] = [cat_val[0] for cat_val in stat_cat_val]
        data['mean_max_salary'] = [round(cat_val[1], -3) for cat_val in stat_cat_val]
        data['mean_min_salary'] = [round(cat_val[2], -3) for cat_val in stat_cat_val]
        return data

    def get_max_salaries(self, date, tag_name):
        """ Return list of max salaries. """
        stat = self.get_statistics(date)
        return stat.max_salaries[tag_name]


@app.before_request
def before_request():
    """ Connect to db before each request. """
    g.db = WebDbConnector(app.db_manager)


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
    mean_max_salary.sort(key=lambda date_salary: date_salary[0])
    mean_min_salary.sort(key=lambda date_salary: date_salary[0])
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
    # TODO: if we get sqlalchemy.exc.ProgrammingError - show message
    return render_template('gallery.html',
                           dates=g.db.get_timestamps_and_dates(),
                           tags=skills.TAG_NAMES)


@app.route('/tag/')
def tag_view():
    """ Show statistics on specific tag. """
    tag_name = request.args.get('tag', "python", type=str)
    return render_template('lang.html', dates=g.db.get_timestamps_and_dates(),
                           tag_name=tag_name)


def start_server(db_name=cfg.DB_NAME):
    """ Start server. """
    app.db_manager = data_model.DBEngine(db_name)
    app.run(host='0.0.0.0', port=cfg.PORT, debug=cfg.WEB_DEBUG)


if __name__ == '__main__':
    start_server()
