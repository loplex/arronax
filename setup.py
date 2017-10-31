#!/usr/bin/env python
#-*- coding: utf-8-*-
#
# Arronax - a application and filemananer plugin to create and modify .desktop files
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
from setuptools import setup, find_packages

from deb_setup_helpers import (get_deb_version, get_deb_description)

def read_from_file(path):
    with open(path) as input:
        return input.read()


setup(
    name='arronax',
    version=get_deb_version(full=False),
    packages=find_packages(),
    include_package_data=True,
    maintainer='Florian Diesch',
    maintainer_email='devel@florian-diesch.de',
    author = "Florian Diesch",
    author_email = "devel@florian-diesch.de",    
    description=get_deb_description(),
    long_description=read_from_file(
        'README.txt',
        ),
    license='GPLv3',
    url='http://www.florian-diesch.de/software/arronax/',
    download_url='http://www.florian-diesch.de/software/arronax/',
    data_files=[
        ('/usr/share/arronax/ui/',
         glob.glob('data/ui/*.ui')),
        ('/usr/share/arronax/icons/',
         glob.glob('data/icons/*.png')),
        ('/usr/share/applications',
         glob.glob('data/desktop/*.desktop')),
        ('/usr/share/nautilus-python/extensions/',
         glob.glob('nautilus/*.py')),
        ('/usr/share/nemo-python/extensions/',
         glob.glob('nemo/*.py')),
        ('/usr/share/caja-python/extensions/',
         glob.glob('caja/*.py')),
        ],
    entry_points = {
        'console_scripts': ['arronax=arronax.editor:main'],
        },
    keywords = "Nautilus, Nemo, Caja, extension, plugin, starter, desktop", 
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: Gnome',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Utilities',
        ],
    )
