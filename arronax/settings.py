import os, os.path, subprocess
from gi.repository import GLib



if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')

DEFAULT_ICON = '/usr/share/icons/hicolor/scalable/apps/gnome-panel-launcher.svg'

USER_APPLICATIONS_DIR = os.path.join(GLib.get_user_data_dir(), 'applications/')
USER_DESKTOP_DIR = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DESKTOP)

LAST_ICON = DEFAULT_ICON 


