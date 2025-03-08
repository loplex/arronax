#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#

import arronax
import arronax.settings
import os.path
import sys

fullpath = os.path.abspath(__file__)
path = os.path.split(fullpath)[0]
sys.path = [path] + sys.path

DATA_DIR = os.path.normpath(os.path.join(path, 'data'))

arronax.settings.DATA_DIR = DATA_DIR
arronax.settings.UI_DIR = os.path.join(DATA_DIR, 'ui')

arronax.main()
