import os, os.path
#from gi.repository import GLib
#from gettext import gettext as _
import xdgapp
import xdg.BaseDirectory

APP_NAME = 'Arronax'
APP_VERSION  = '0.01'

if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')

_xdg_app = xdgapp.XdgApplication( APP_NAME.lower(), create_dirs=False )



USER_APPLICATIONS_DIR = os.path.join(xdg.BaseDirectory.xdg_data_home, 
                                     'applications/')

#USER_DESKTOP_DIR = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DESKTOP)
try:
    USER_DESKTOP_DIR = _xdg_app.get_data_path( 'desktop', '~/Desktop' )
except UnboundLocalError:  # Workaround for bug in xdgapp
    USER_DESKTOP_DIR = os.path.expanduser('~/Desktop/')

DEFAULT_ICON = '/usr/share/icons/hicolor/scalable/apps/nautilus.svg'
DEFAULT_ICON_SIZE = 48
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')

LAST_ICON = DEFAULT_ICON 
LAST_FILENAME = DEFAULT_FILENAME

GETTEXT_DOMAIN='arronax'

