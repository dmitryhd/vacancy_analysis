#!/usr/bin/env python3

import unittest

from igallery import app

class TestServer(unittest.TestCase):
    """ Basic test of main page view. """
    def setUp(self):
        """ Init test app """
        self.app = app.test_client()

    def test_index(self):
        """ Check if images are in main page. """
        res = self.app.get('/')
        assert 'iGallery' in str(res.data), str(res.data)
        assert '<img' in str(res.data), str(res.data)

unittest.main()

