import os, os.path
import xdgpath
import xdg.BaseDirectory
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
from gettext import gettext as _
import gettext

APP_NAME = 'Arronax'
APP_VERSION  = '0.06'

app_name = APP_NAME.lower()

if os.path.isfile('.is-devel-dir'):
    DATA_DIR = 'data'
else: 
    DATA_DIR = '/usr/share/arronax'

UI_DIR = os.path.join(DATA_DIR, 'ui')


USER_APPLICATIONS_DIR = os.path.join(xdg.BaseDirectory.xdg_data_home, 
                                     'applications/')

SYS_APPLICATIONS_DIR = '/usr/share/applications/'

USER_DESKTOP_DIR = xdgpath.get_user_dir( 'desktop', '~/Desktop' )
USER_AUTOSTART_DIR = os.path.join(
    xdg.BaseDirectory.xdg_config_home, 'autostart')

SYS_AUTOSTART_DIR = os.path.join('etc', 'xdg', 'autostart')
try:
    for dir in xdg.BaseDirectory.xdg_config_dirs[1:]:
        path = os.path.join(dir, 'autostart')
        if os.path.isdir(path):
            SYS_AUTOSTART_DIR = path
            break
except:
    pass

DEFAULT_ICON='system-file-manager'

DEFAULT_ICON_SIZE = 64
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')

#LAST_ICON = DEFAULT_ICON 
LAST_FILENAME = DEFAULT_FILENAME

GETTEXT_DOMAIN='arronax'

WEB_URL = 'http://www.florian-diesch.de/software/%s/' % app_name
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DJCGEPS4746PU'
FLATTR_URL = 'https://flattr.com/thing/712282/Arronax'
TRANSLATIONS_URL = 'https://translations.launchpad.net/%s' % app_name
BUGREPORT_URL = 'https://bugs.launchpad.net/%s/+filebug' % app_name
QUESTION_URL = 'https://answers.launchpad.net/%s/+addquestion' % app_name


KNOWN_DESKTOPS={'GNOME': _('GNOME'),
                'KDE': _('KDE'), 
                'LXDE': _('LXDE'),
                'MATE': _('MATE'),
                'Razor': _('Razor-qt'),
                'ROX': _('ROX'),
                'TDE': _('Trinity Desktop'),
                'Unity': _('Unity'), 
                'XFCE': _('XFCE'),
                'Old': _('Legacy environments')
            }

