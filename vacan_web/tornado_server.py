#!/usr/bin/env python3

"""
- jinja(?) template
- static files
TODO: try: tornado https://github.com/bueda/tornado-boilerplate
"""

import tornado.web
import tornado.ioloop

import os.path as path

DEFAULT_PORT = 8888

static_path = path.join(path.dirname(path.abspath(__file__)), 'static/')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")


def make_app():
    handlers = [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
            (r'/', MainHandler)
    ]
    app = tornado.web.Application(handlers)
    return app


if __name__ == '__main__':
    app = make_app()
    app.listen(DEFAULT_PORT)
    tornado.ioloop.IOLoop.current().start()
