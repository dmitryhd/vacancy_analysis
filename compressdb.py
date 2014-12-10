#!/usr/bin/env python3
import glob
import vacancy_processor as vp

for db_file in glob.glob('*.db'):
    vp.compress_database(db_file)
