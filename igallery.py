#!/usr/bin/env python3

""" Just a web server in python + flask. Shows content of folder images. """

from flask import request, Flask, render_template, send_from_directory, jsonify
import os
import glob
import config as cfg

import re
import vacancy_processor as vp
import data_model as dm

app = Flask(__name__)
app.debug = True

def run_server():
    """ Runs gallery. """
    app.run(host='0.0.0.0', port=cfg.PORT)


# --------------- AJAX ------------------
@app.route('/_get_plots')
def get_plots():
    """ """
    images = glob.glob(cfg.PLOT_PATH + '*.jpg')
    images.extend(glob.glob(cfg.PLOT_PATH + '*.png'))
    images = sorted(images, reverse=True)
    plots = []
    for img in images:
        tail, filename = os.path.split(img)
        plots.append('/plots/' + filename)
    return jsonify(images=plots)


@app.route('/_get_plot_data')
def get_plot_data():
    """ """
    plot_name = request.args.get('plot', "", type=str)
    print('plot_name', plot_name)
    seconds = int(re.search(r'(\d+)', plot_name).groups()[0])
    print('----------------')
    print('seconds', seconds)
    s = vp.prepare_db('data/stat.db')
    q = s.query(dm.ProcessedStatistics)
    proc_vac = {}
    for res in q:
        proc_vac[res.date] = res.get_tag_bins()
        print(res.date, res.get_tag_bins())

    categories = [tag[0] for tag in cfg.TAGS]
    print('proc_vac:', proc_vac)
    tag_bins = proc_vac[seconds]
    _from = []
    to = []
    for cat in categories:
        _from.append(tag_bins[cat])
        to.append(tag_bins[cat])
    print(categories, _from, to)
    return jsonify(d_categories=categories, d_from=_from, d_to=to)
# -------------- END AJAX ----------------


@app.route('/')
def hello_world():
    """ Index view. """
    return render_template('gallery.html')


@app.route('/plots/<path:filename>')
def send_foo(filename):
    return send_from_directory('./plots/', filename)


def main():
    """ Parse command line arguments. """
    run_server()


if __name__ == '__main__':
    main()
