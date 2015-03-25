#!/usr/bin/env python3

""" General test preparations and constants. """

import vacan.processor.statistics as stat
import vacan.processor.data_model as dm
import vacan.common.tag_config as tag_cfg


REF_TIME = 10000000
TEST_DATA_DIR = 'test_data/'
REF_NUMBER_OF_VACANCIES = {'java': 1, 'c++': 3, 'python': 1}
REF_MIN_SALARIES = {'c++': [10000, 11000, 9000], 'java': [10000], }
REF_MAX_SALARIES = {'java': [15000], 'c++': [15000, 16000, 14000]} 
# TODO: this is too straightforward
REF_MEAN_MIN_SALARIES = {'c++': 10000.0, 'java': 10000.0, 'perl': 0}
REF_MEAN_MAX_SALARIES = {'perl': 0, 'c++': 15000, 'java': 15000}


def create_fictive_database(db_name):
    """ Return database manager pointing to newly created database with one
        certain statistics represented in constants above.
    """
    db_manager = dm.DatabaseManager(db_name, 'w')
    raw_vac_session = db_manager.get_session()
    raw_vacs = [dm.RawVacancy('1', '<td class="l-content-colum-1 b-v-info-content">java c++ от 10 000 до 15 000 </td>'),
                dm.RawVacancy('2', '<td class="l-content-colum-1 b-v-info-content">c++ от 11 000 до 16 000 </td>'),
                dm.RawVacancy('3', '<td class="l-content-colum-1 b-v-info-content">c++ от 9 000 до 14 000 </td>'),
                dm.RawVacancy('4', '<td class="l-content-colum-1 b-v-info-content">python от 15 000 </td>')]
    raw_vac_session.add_all(raw_vacs)
    raw_vac_session.commit()
    proc_vacs = dm.process_vacancies_from_db(raw_vac_session, tag_cfg.TAGS)
    ref_proc_stat = stat.ProcessedStatistics(proc_vacs, _time=REF_TIME)
    ref_proc_stat.calculate_all()
    raw_vac_session.add(ref_proc_stat)
    raw_vac_session.commit()
    raw_vac_session.close()
    return db_manager
