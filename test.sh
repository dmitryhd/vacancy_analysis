#!/bin/bash
cd web_interface
nosetests -v test.py
cd ../processor
nosetests -v test.py
