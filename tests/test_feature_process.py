#!/usr/bin/env python3

""" Unittest file for features. """

import unittest

import vacan.processor.features as ft
import vacan.processor.data_model as dm


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
        

class TestProcessor(unittest.TestCase):
    """ Test case: TestProcessor. """

    def test_simple_processing(self):
        """ TestProcessor: test process some vacs. Ensure delete duplicates"""
        test_features = {'lang': {'java': '', 'c++': r'(^|\s)c\+\+($|\s)',
                                  'python': ''}}
        qualifier = ft.Qualifier(test_features)
        processor = ft.VacancyProcessor(qualifier)
        self.assertTrue(processor)
        vac1_html = ('c++ python '
                     '<td class="l-content-colum-1 b-v-info-content">'
                     'от 90 000 до 100 000</td>'
                     '<td class="l-content-colum-3 b-v-info-content">1 3</td>')
        vac2_html = ('python '
                     '<td class="l-content-colum-1 b-v-info-content">'
                     'до 110 000</td>'
                     '<td class="l-content-colum-3 b-v-info-content">2 6</td>')
                    

        raw_vacs = [dm.RawVacancy('vac1', vac1_html, 'url1'), 
                    dm.RawVacancy('vac1', vac1_html, 'url1'),
                    dm.RawVacancy('vac2', vac2_html, 'url2')]
        proc_vacs = processor.process(raw_vacs)
        self.assertEqual(len(proc_vacs), 2)
        self.assertEqual(proc_vacs[0].features,
                         {'c++': True, 'python': True, 'java': False})
        self.assertEqual(proc_vacs[1].features,
                         {'c++': False, 'python': True, 'java': False})
        self.assertEqual((proc_vacs[0].min_sal, proc_vacs[0].max_sal),
                         (90000, 100000))
        self.assertEqual((proc_vacs[1].min_sal, proc_vacs[1].max_sal),
                         (None, 110000))
        self.assertEqual((proc_vacs[0].min_exp, proc_vacs[0].max_exp),
                         (1, 3))
        self.assertEqual((proc_vacs[1].min_exp, proc_vacs[1].max_exp),
                         (2, 6))
