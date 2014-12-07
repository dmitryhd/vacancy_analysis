#!/bin/bash
pwd

# Delete all plots and data/stat.db
rm -rfv plots/*
rm -v data/stat.db

# Create them anew.
for i in data/*.db; do
    echo "./vacancy_processor.py -p -d $i;"
    ./vacancy_processor.py -p -d $i;
done
for i in data/*.tgz; do 
    echo "./vacancy_processor.py -c -p -d $i;"
    ./vacancy_processor.py -c -p -d $i;
done
