#!/usr/bin/env python3

""" Unittest file for migration from sqlite. """

import unittest
from tests import *

import vacan.processor.data_model as dm
import vacan.processor.statistics as stat
import vacan.processor.migrate as migr


class TestMigration(unittest.TestCase):
    """ Testing migration from sqlite to mysql. """
    test_db = 'vacan_test_migrate'

    @classmethod
    def tearDownClass(cls):
        dm.delete_mysql_db(cls.test_db)

    def test_untar(self):
        """ Migration: decompress sqlite archive. """
        migrator = migr.Migrator()
        fname = migrator.untar_file('test_data/compr_raw_vac_ex.db.tgz')
        self.assertEqual(fname, '/tmp/vac_1426497962.db')

    def test_get_raw_vacs(self):
        """ Migration: get raw vacs from compressed sqlite. """
        migrator = migr.Migrator()
        vacs = migrator.get_raw_vacs('test_data/compr_raw_vac_ex.db.tgz')
        self.assertTrue(vacs)
        self.assertGreater(len(vacs), 5)
    
    def test_migrate(self):
        """ Migration: Migrate one collection set into mysql from sqlite. """
        migrator = migr.Migrator()
        migrator.migrate('test_data/', self.test_db)
        db_manager = dm.DatabaseManager(self.test_db)
        session = db_manager.get_session()
        migrated_vacs = session.query(dm.RawVacancy)
        self.assertTrue(migrated_vacs)
        self.assertGreater(len(list(migrated_vacs)), 5)
        statistics = session.query(stat.ProcessedStatistics)
        self.assertTrue(statistics)
        self.assertEqual(len(list(statistics)), 1)
        session.close()
        db_manager.dispose()
        

