#!/bin/bash
pwd

# Delete all plots and data/stat.db
rm -rfv plots/*
rm -v data/stat.db
rm -v data/stat.db.tgz

for i in data/*.tgz; do
    echo "./vacancy_processor.py -c -p -d $i;"
    ./vacancy_processor.py -c -p -d $i;
done

rm -v data/stat.db.tgz
