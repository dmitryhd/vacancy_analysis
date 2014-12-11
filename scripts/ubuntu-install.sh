#!/bin/bash
# installation tested on Ubuntu 14.04 clean
sudo apt-get install python3-pip
sudo apt-get install r-base
sudo apt-get install uwsgi
sudo apt-get install uwsgi-plugin-python3
sudo pip3 install BeautifulSoup4
sudo pip3 install sqlalchemy
sudo pip3 install flask
./test.py
