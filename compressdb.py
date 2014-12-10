#!/usr/bin/env python3
import glob
import vacancy_processor as vp

for db_file in glob.glob('data/*.db'):
    print('compress', db_file)
    vp.compress_database(db_file)
