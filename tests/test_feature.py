#!/usr/bin/env python3

""" Unittest file for features. """

import unittest

import vacan.processor.features as ft


class TestFeature(unittest.TestCase):
    """ Save some processed data. """

    def test_features_create(self):
        """ TestFeature: creation. """
        c_skill = ft.Feature('c', 'lang', r"(^|\s)c($|\s)")
        java_skill = ft.Feature('java')
        javatext = 'i can do java'
        ctext = 'i can do c'
        self.assertTrue(c_skill.is_present(ctext))
        self.assertFalse(c_skill.is_present(javatext))
        self.assertTrue(java_skill.is_present(javatext))
        self.assertFalse(java_skill.is_present(ctext))
    # test for c++ jere


class TestQualifier(unittest.TestCase):
    """  """
    def test_basic_analize(self):
        """ TestQualifier: basic analize """
        test_features = {'lang': {'java': '', 'c++': r'(^|\s)c\+\+($|\s)',
                                  'python': ''}}
        qualifier = ft.Qualifier(test_features)
        self.assertTrue(qualifier.features)
        text = 'we need a nice c++ and java coder' 
        features = qualifier.analyze(text)
        self.assertTrue(features)
        self.assertEqual(features, {'c++': True, 'java': True,
                                    'python': False})
        

        

