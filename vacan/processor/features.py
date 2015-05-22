#!/usr/bin/env python3

""" Text categories by skill. """

import re


class Feature(object):
    """  """
    def __init__(self, name, category='', regexp=None):
        self.name = name
        self.regexp = regexp if regexp else r'(^|\s){}($|\s)'.format(name)
        self.category = category

    def is_present(self, text):
        return bool(re.search(self.regexp, text))
        

class Qualifier(object):
    """docstring for Qu"""
    def __init__(self, feature_dict):
        self.features = {}
        for category, features in feature_dict.items():
            for name, regexp in features.items():
                self.features[name] = Feature(name, category, regexp)

    def normalize(self, text):
        return text.lower()

    def analyze(self, text):
        norm_text = self.normalize(text)
        text_features = {}
        for feature in self.features.values():
            text_features[feature.name] = feature.is_present(norm_text)
        return text_features

        
