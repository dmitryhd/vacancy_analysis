#!/usr/bin/env python3

from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
import vacan

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'vacancy_analysis',
    version = vacan.__version__,
    description = 'Web crawler and data analizer with web interface.'
                  'Currently used to gather information about programmer '
                  'vacancies.',
    long_description=long_description,
    url = 'https://github.com/dmitryhd/vacancy_analysis',
    # Author details
    author='Dmitriy Khodakov',
    author_email = 'dmitryhd@gmail.com',
    # Choose your license
    license = 'MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='crawler data analysis text processing',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs']),
    # List run-time dependencies here.  These will be installed by pip when

    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['flask', 'BeautifulSoup4', 'sqlalchemy', 'requests', 
                      'pymysql', 'flask-restful',
                      'sqlalchemy_utils'],
    # TODO: sudo mkdir /opt/vacan/data/; chmod a+rw /opt/vacan/data/
    # TODO: yum -y install mariadb-server mariadb
    # systemctl enable mariadb
    # mysqladmin -u root password 'new-password'   
    # in mysqlconsole: CREATE USER 'vacan'@'localhost' IDENTIFIED BY 'vacan';
    # GRANT ALL PRIVILEGES ON vacan . * TO 'vacan'@'localhost';
    # GRANT ALL PRIVILEGES ON vacan_t . * TO 'vacan'@'localhost';
    # GRANT ALL PRIVILEGES ON vacan_raw_t . * TO 'vacan'@'localhost';
    # GRANT ALL PRIVILEGES ON vacan_t_tmp . * TO 'vacan'@'localhost';
    # /etc/my.conf
#[client]
#default-character-set=utf8
#[mysqld]
#character-set-server = utf8

    # List additional groups of dependencies here (e.g. development
    # dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    include_package_data = True,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    scripts=['bin/vacan.download', 'bin/vacan.monitor'],
)
