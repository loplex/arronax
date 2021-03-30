#!/usr/bin/env python3
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


setup(
    packages=find_packages(),
    include_package_data=True,

    data_files=[
        ('share/man/man1',
         glob.glob('data/man/*.1')),
        ('share/arronax/ui/',
         glob.glob('data/ui/*.ui')),
        ('share/applications',
         glob.glob('data/desktop/*.desktop')),
        ('share/nautilus-python/extensions/',
         glob.glob('plugins/nautilus-arronax.py')),
        ('share/nemo-python/extensions/',
         glob.glob('plugins/nemo-arronax.py')),
        ('share/caja-python/extensions/',
         glob.glob('plugins/caja-arronax.py')),
        ('share/thunarx-python/extensions/',
         glob.glob('plugins/thunar-arronax.py')),
        ('share/icons/hicolor/scalable/apps/',
         ['data/icons/arronax.svg']),
        ] + \
        [('share/locale/%s/LC_MESSAGES/'%mo.split('/')[2], [mo])
             for mo in glob.glob('data/mo/*/arronax.mo')] + \
        [('share/icons/hicolor/{s}x{s}'.format(s=i.split('/')[2]), [i])
             for i in glob.glob('data/icons/*/arronax.png')], 

    entry_points = {

        'console_scripts': ['arronax=arronax.editor:main'],
        },
    keywords = "Nautilus, Nemo, Caja, extension, plugin, starter, desktop", 
    classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        ],
    )
