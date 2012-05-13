import os, os.path, subprocess


if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')


LAST_ICON = '/usr/share/icons/hicolor/'
