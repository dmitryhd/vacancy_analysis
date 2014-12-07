#!/usr/bin/env python3
# pylint: disable=invalid-name
""" Just a web server in python + flask. Shows content of folder images. """

import os
import glob
from flask import request, Flask, render_template, send_from_directory, jsonify

import config as cfg
import data_model as dm
import vacancy_processor as vp

app = Flask(__name__)
app.debug = True

def run_server():
    """ Runs gallery. """
    app.run(host='0.0.0.0', port=cfg.PORT)


# --------------- AJAX ------------------
@app.route('/_get_plots')
def get_plots():
    """ Serve list of all plot filenames as json. """
    images = glob.glob(cfg.PLOT_PATH + '*.jpg')
    images.extend(glob.glob(cfg.PLOT_PATH + '*.png'))
    images = sorted(images, reverse=True)
    plots = []
    for img in images:
        tail, filename = os.path.split(img)
        plots.append('/plots/' + filename)
    return jsonify(images=plots)


@app.route('/_get_statistics')
def get_statistics():
    """ Serve statistics as json.
        Plot file name given by request.
    """
    plot_name = request.args.get('plot', "", type=str)
    # Get timestamp from plot to search database for statistics.
    timestamp = vp.get_time_by_filename(plot_name)
    statistics_db = dm.open_db('data/stat.db', 'r')
    stat = statistics_db.query(
        dm.ProcessedStatistics).filter_by(date=timestamp).one()

    categories = [tag.name for tag in cfg.TAGS]
    stat_cat_val = zip(categories,
                       [stat.get_tag_bins()[cat] for cat in categories])
    stat_cat_val = list(stat_cat_val)
    stat_cat_val.sort(key=lambda cat_val: cat_val[1], reverse=True)  # by val
    categories = [cat_val[0] for cat_val in stat_cat_val]
    values = [cat_val[1] for cat_val in stat_cat_val]
    return jsonify(d_categories=categories, d_values=values)


@app.route('/plots/<path:filename>')
def serve_plots(filename):
    """ Static function to serve png plots. """
    return send_from_directory('./plots/', filename)
# -------------- END AJAX ----------------


@app.route('/')
def hello_world():
    """ Index view. """
    return render_template('gallery.html')


def main():
    """ Parse command line arguments. """
    run_server()


if __name__ == '__main__':
    main()
