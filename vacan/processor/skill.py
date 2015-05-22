#!/usr/bin/env python3

""" Text categories by skill. """

import re


class Skill(object):
    """  """
    def __init__(self, name, category='', regexp=None,):
        self.name = name
        self.regexp = regexp if regexp else name
        self.category = category

    def is_present(self, text):
        return bool(re.search(self.regexp, text))
        
