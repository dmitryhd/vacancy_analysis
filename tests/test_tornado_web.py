#!/usr/bin/env python3

""" """


from tornado.testing import AsyncHTTPTestCase

import tornado_server


class TestWebApp(AsyncHTTPTestCase):
    def get_app(self):
        return tornado_server.make_app()

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'Hello world')

    def test_get_vacancies(self):
        response = self.fetch('/api/get-vacancies/')
        self.assertEqual(response.code, 200)

    def test_static(self):
        response = self.fetch('/static/vacan-style.css')
        self.assertEqual(response.code, 200)
