#!/usr/bin/env python3

""" Just a web server in python + flask. Shows content of folder images. """

from flask import request, Flask, render_template, send_from_directory, jsonify
import sys
import os
import glob

PORT = 9999
app = Flask(__name__)
app.debug = True
PLOT_PATH = './plots/'

def run_server():
    """ Runs gallery. """
    app.run(host='0.0.0.0', port=PORT)

@app.route('/_get_plots')
def get_plots():
    images = glob.glob(PLOT_PATH + '*.jpg')
    images.extend(glob.glob(PLOT_PATH + '*.png'))
    images = sorted(images, reverse=True)
    plots = []
    for img in images:
        tail, filename = os.path.split(img)
        plots.append('/plots/' + filename)
    return jsonify(images=plots)

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
