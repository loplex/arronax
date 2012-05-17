import os, os.path, subprocess
from gi.repository import GLib
from gettext import gettext as _


APP_NAME = 'Arronax'
APP_VERSION  = '0.01'

if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')



USER_APPLICATIONS_DIR = os.path.join(GLib.get_user_data_dir(), 'applications/')
USER_DESKTOP_DIR = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DESKTOP)

DEFAULT_ICON = '/usr/share/icons/hicolor/scalable/apps/gnome-panel-launcher.svg'
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')

LAST_ICON = DEFAULT_ICON 
LAST_FILENAME = DEFAULT_FILENAME

GETTEXT_DOMAIN='arronax'

