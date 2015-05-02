#!/usr/bin/env python3

""" Database migration from sqlite to mysql helper class. 
    Author: Dmitriy Khodakov <dmitryhd@gmail.com>
    Date: 29.09.2014
"""
import os
import glob
import subprocess
import sqlalchemy

import vacan.processor.statistics as stat
import vacan.processor.data_model as dm
import vacan.utility as util
import vacan.skills as skills
import vacan.processor.vacancy_processor


class Migrator(object):
    """ Database migration from sqlite to mysql helper class. """

    def untar_file(self, archive_name):
        """ Return file descriptor of unterred db. """
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
        db_name = self.untar_file(archive_name)
        engine = sqlalchemy.create_engine('sqlite:///' + db_name, echo=False)
        session = sqlalchemy.orm.sessionmaker(bind=engine)()
        res = session.query(dm.RawVacancy)
        res = list(res)
        session.close()
        engine.dispose()
        print('get vacs from: ', db_name, ' number: ', len(res))
        return list(res)

    def process_chunk(self, archive_name):
        raw_vacs = self.get_raw_vacs(archive_name)
        gather_time_sec = util.get_time_by_filename(archive_name)
        print('Get time: ', gather_time_sec)
        processed_vacancies = vacan.processor.vacancy_processor.process_vacancies(raw_vacs, skills.SKILLS)
        proc_stat = stat.ProcessedStatistics(processed_vacancies,
                                             gather_time_sec)
        print('Get time date:',  util.int_to_date(gather_time_sec))
        for raw_vac in raw_vacs:
            raw_vac.date = util.int_to_date(gather_time_sec)
        proc_stat.calculate_all()
        return proc_stat, raw_vacs

    def migrate(self, archive_dir, new_db_name):
        with dm.DBEngine(new_db_name, 'w').get_session() as session:
            for arch_name in glob.glob(archive_dir + '*.tgz'):
                proc_stat, raw_vacs = self.process_chunk(arch_name)
                print('Writing to new db:', len(raw_vacs), 'vacancies')
                for raw_vac in raw_vacs:
                    raw_vac.id += util.date_to_int(raw_vac.date)
                    session.merge(raw_vac)
                    session.commit()
                session.add(proc_stat)
                session.commit()
