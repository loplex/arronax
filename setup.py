#!/usr/bin/env python
#-*- coding: utf-8-*-
#
# Arronax - a Nautilus plugin to create and modify .desktop files
#
# Copyright (C) 2012 Florian Diesch <devel@florian-diesch.de>
#
# Homepage: http://www.florian-diesch.de/software/arronax/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import glob

import distribute_setup
distribute_setup.use_setuptools()


from setup_helpers import (
    description, find_doctests, get_version, long_description, require_python)
from setuptools import setup, find_packages

from DistUtilsExtra.command import *

require_python(0x20600f0)
__version__ = '0.01'


setup(
    name='arronax',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    maintainer='Florian Diesch',
    maintainer_email='devel@florian-diesch.de',
    author = "Florian Diesch",
    author_email = "devel@florian-diesch.de",    
    description='Nautilus plugin to create and modify .desktop files',
    long_description=long_description(
        'README.txt',
        ),
    license='GPLv3',
    url='http://www.florian-diesch.de/software/arronax/',
    download_url='http://www.florian-diesch.de/software/arronax/',
    data_files=[
        ('share/arronax/ui/',
         glob.glob('data/ui/*.ui')),
        ('share/arronax/icons/',
         glob.glob('data/icons/*.svg')),
        ('share/applications',
         glob.glob('data/desktop/*.desktop')),
        ('share/nautilus-python/extensions/',
         ['arronax/nautilus-arronax.py']),
        ],
    entry_points = {
        'console_scripts': ['arronax=arronax.editor:main'],
        },
    keywords = "Nautilus, extension, plugin, starter, desktop", 
    classifiers=[
     'Development Status :: 3 - Alpha',
     'Environment :: X11 Applications :: Gnome',
     'Intended Audience :: End Users/Desktop',
     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
     'Natural Language :: English',
     'Natural Language :: German',
     'Operating System :: POSIX :: Linux',
     'Programming Language :: Python',
     'Topic :: Desktop Environment :: File Managers',
     'Topic :: Desktop Environment :: Gnome',
     'Topic :: Utilities',
        ],
    cmdclass = { "build" : build_extra.build_extra,
                 "build_i18n" :  build_i18n.build_i18n,
                 "build_help" :  build_help.build_help,
                 "build_icons" :  build_icons.build_icons }
    )
