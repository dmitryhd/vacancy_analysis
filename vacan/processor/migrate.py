#!/usr/bin/env python3

"""
Database migration from sqlite to mysql helper class.
TODO: this module is kinda deprecated.
Author: Dmitriy Khodakov <dmitryhd@gmail.com>
"""
import os
import glob
import subprocess
import sqlalchemy

import vacan.processor.statistics as stat
import vacan.processor.data_model as dm
import vacan.utility as util
import vacan.skills as skills
import vacan.processor.vacancy_processor as proc


class Migrator(object):
    """ Database migration from sqlite to mysql helper class. """

    @staticmethod
    def untar_file(archive_name):
        """ Return file descriptor of untarred db. """
        os.system("tar xf " + archive_name)
        db_name = subprocess.check_output(["tar", "-tf", archive_name])
        db_name = db_name.decode('utf8')
        db_name = db_name.strip()
        mv_command = "mv " + db_name + " /tmp/"
        os.system(mv_command)
        db_name = os.path.basename(db_name)
        os.system("rm -rf opt/")
        return "/tmp/" + db_name

    def get_raw_vacs(self, archive_name):
        """ Return list of raw vacs in given archive. """
        db_name = self.untar_file(archive_name)
        print(db_name)
        with dm.DBEngine(db_name, dbtype='sqlite').get_session() as session:
            raw_vacs = list(session.query(dm.RawVacancy))
            session.expunge_all()
        print('get vacs from: ', db_name, ' number: ', len(raw_vacs))
        return raw_vacs

    def process_chunk(self, archive_name):
        """ Return proc stat and raw vacs for given archive. """
        raw_vacs = self.get_raw_vacs(archive_name)
        gather_time_sec = util.get_time_by_filename(archive_name)
        processed_vacancies = proc.process_vacancies(raw_vacs, skills.SKILLS)
        proc_stat = stat.ProcessedStatistics(processed_vacancies,
                                             gather_time_sec)
        print('Processed from date:', util.int_to_date(gather_time_sec))
        for raw_vac in raw_vacs:
            raw_vac.date = util.int_to_date(gather_time_sec)
        proc_stat.calculate_all()
        return proc_stat, raw_vacs

    def migrate(self, archive_dir, db_engine):
        """ Sets all raw vacancies from archive dir to new_db_name. """
        with db_engine.get_session() as session:
            for arch_name in glob.glob(archive_dir + '*.tgz'):
                #try:
                proc_stat, raw_vacs = self.process_chunk(arch_name)
                #except sqlalchemy.exc.OperationalError:
                    # No such table.
                #    print('no such table for {}, skip it.'.format(arch_name))
                #    continue
                print('Writing to new db:', len(raw_vacs), 'vacancies')
                for raw_vac in raw_vacs:
                    raw_vac.id += util.date_to_int(raw_vac.date)
                    try:
                        session.merge(raw_vac)
                        session.commit()
                    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
                        session.rollback()
                        print('Duplicate entry. Skip.')
                session.add(proc_stat)
                session.commit()


def run_migration(folder_name, db_name):
    """ Migrate from folder to db_name. """
    migrator = Migrator()
    db_manager = dm.DBEngine(db_name, mode='w')
    migrator.migrate(folder_name, db_manager)
