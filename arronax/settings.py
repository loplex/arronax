import os, os.path
import xdgpath
import xdg.BaseDirectory

APP_NAME = 'Arronax'
APP_VERSION  = '0.03'

if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')


USER_APPLICATIONS_DIR = os.path.join(xdg.BaseDirectory.xdg_data_home, 
                                     'applications/')

SYS_APPLICATIONS_DIR = '/usr/share/applications/'

USER_DESKTOP_DIR = xdgpath.get_user_dir( 'desktop', '~/Desktop' )

DEFAULT_ICON = '/usr/share/icons/hicolor/scalable/apps/nautilus.svg'
DEFAULT_ICON_SIZE = 48
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')

LAST_ICON = DEFAULT_ICON 
LAST_FILENAME = DEFAULT_FILENAME

GETTEXT_DOMAIN='arronax'

