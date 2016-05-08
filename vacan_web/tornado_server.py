#!/usr/bin/env python3

"""
- jinja(?) template
- static files
TODO: try: tornado https://github.com/bueda/tornado-boilerplate
"""

import tornado.web
import tornado.ioloop
import json
import pandas as pd

import os.path as path

DEFAULT_PORT = 8888

static_path = path.join(path.dirname(path.abspath(__file__)), 'static/')

vacancies = pd.read_csv(path.join(static_path, 'vacancies_done.csv'),
                        header=0, sep='|')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")


class Vacancies(tornado.web.RequestHandler):
    def get(self):
        vacs = vacancies.to_dict(orient='list')
        self.write(json.dumps(vacs))

def make_app():
    handlers = [
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        (r'/', MainHandler),
        (r'/api/get-vacancies/', Vacancies),
    ]
    app = tornado.web.Application(handlers)
    return app


if __name__ == '__main__':
    app = make_app()
    app.listen(DEFAULT_PORT)
    tornado.ioloop.IOLoop.current().start()
