#!/usr/bin/env python3

""" Unittest file for skill. """

import unittest

from vacan.processor.skill import Skill

class TestSkill(unittest.TestCase):
    """ Save some processed data. """

    def test_skill_create(self):
        """ TestSkill: creation. """
        c_skill = Skill('c', r"\bc\b")
        java_skill = Skill('java')
        javatext = 'i can do java'
        ctext = 'i can do c'
        self.assertTrue(c_skill.is_present(ctext))
        self.assertFalse(c_skill.is_present(javatext))
        self.assertTrue(java_skill.is_present(javatext))
        self.assertFalse(java_skill.is_present(ctext))

    # test for c++ jere

