import os, os.path
import xdgpath
import xdg.BaseDirectory
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
from gettext import gettext as _

APP_NAME = 'Arronax'
APP_VERSION  = '0.05'

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

DEFAULT_ICON = '/usr/share/icons/hicolor/scalable/apps/nautilus.svg'
if not os.path.isfile(DEFAULT_ICON):
    DEFAULT_ICON='system-file-manager'

DEFAULT_ICON_SIZE = 48
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')

LAST_ICON = DEFAULT_ICON 
LAST_FILENAME = DEFAULT_FILENAME

GETTEXT_DOMAIN='arronax'

WEB_URL = 'http://www.florian-diesch.de/software/%s/' % app_name
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DJCGEPS4746PU'
FLATTR_URL = 'https://flattr.com/thing/712282/Arronax'
TRANSLATIONS_URL = 'https://translations.launchpad.net/%s' % app_name
BUGREPORT_URL = 'https://bugs.launchpad.net/%s/+filebug' % app_name
QUESTION_URL = 'https://answers.launchpad.net/%s/+addquestion' % app_name

FILE_DLG_DEF = {
    'dlg_open': {'title': _('Open File'),
                 'action':  Gtk.FileChooserAction.OPEN,
                 'patterns': ['*.desktop', '*'],
                 'buttons': [(_('Desktop'), USER_DESKTOP_DIR),
                             (_('User App Folder'), USER_APPLICATIONS_DIR),
                             (_('System App Folder'), SYS_APPLICATIONS_DIR),
                             ],
             },
    'dlg_save': {'title': _('Save File'),
             'action':  Gtk.FileChooserAction.SAVE,
             'buttons': [(_('Desktop'), USER_DESKTOP_DIR),
                         (_('User App Folder'), USER_APPLICATIONS_DIR),
                         ],
             },
    'dlg_working_dir': {'title': _('Select Folder'),
                     'action':  Gtk.FileChooserAction.SELECT_FOLDER,
                    },
    'dlg_command': {'title': _('Select Program'),
                'action':  Gtk.FileChooserAction.OPEN,
                },
    'dlg_file': {'title': _('Select File'),
             'action':  Gtk.FileChooserAction.OPEN,
                },
    }

