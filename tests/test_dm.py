#!/usr/bin/env python3

""" Unittest file for Raw vacancy and Processed vacancy. """

import unittest
import vacan.processor.data_model as dm
import vacan.config as cfg
import vacan.common.tag_config as tag_cfg


class TestBasicDataModel(unittest.TestCase):
    """ Test basic datamodel for raw vacancy. """

    def test_raw_vacancy_serialization(self):
        """ BasicDataModel: Writing raw vacancy in db and load it. """
        vac_name = 'test_vac_name'
        vac_html = 'test_vac_html от чч'
        session = dm.DatabaseManager(cfg.DB_NAME_TEST, 'w').get_session()
        vac = dm.RawVacancy(vac_name, vac_html)
        session.add(vac)
        session.commit()
        loaded_vac = session.query(dm.RawVacancy).first()
        self.assertEqual(loaded_vac.name, vac_name)
        self.assertEqual(loaded_vac.html, vac_html)
        self.assertEqual(str(loaded_vac), str(vac))

    def test_processed_vacancy_creation(self):
        """ BasicDataModel: Creating processed vacancy from raw vacancy. """
        test_tags = [tag_cfg.TagRepr('c++', 'c++', 'cpp'),
                     tag_cfg.TagRepr('java', 'java', 'java'),
                     tag_cfg.TagRepr('python', 'python', 'python')]
        vacancy_text = 'needed c++ developer, omg, java so wow'
        vac = dm.RawVacancy('test vacancy', vacancy_text)
        proc_vac = dm.ProcessedVacancy(vac, test_tags)
        self.assertEqual(proc_vac.name, 'test vacancy')
        self.assertTrue(proc_vac.tags[test_tags[0].name])
        self.assertTrue(proc_vac.tags[test_tags[1].name])
        self.assertFalse(proc_vac.tags[test_tags[2].name])
        self.assertTrue('test vacancy' in str(proc_vac))


