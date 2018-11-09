#-*- coding: utf-8-*-
#
# Arronax - a application and filemanager plugin to create and modify .desktop files
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

import os, os.path, sys
from gettext import gettext as _

from arronax import _meta, xdgdirs

APP_TITLE = _meta.TITLE
APP_NAME = _meta.NAME
APP_VERSION = _meta.VERSION
APP_DESC = _meta.DESC
APP_AUTHOR = _meta.AUTHOR_NAME
APP_AUTHOR_EMAIL = _meta.AUTHOR_EMAIL
APP_TIMESTAMP = _meta.TIMESTAMP
APP_YEAR = 2018

app_name = APP_NAME.lower()

GETTEXT_DOMAIN=app_name 

def _create_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
    return path

USER_CONFIG_DIR = _create_dir(os.path.join(xdgdirs.XDG_CONFIG_HOME, app_name))
USER_DATA_DIR   = _create_dir(os.path.join(xdgdirs.XDG_DATA_HOME, app_name))
USER_CACHE_DIR  = _create_dir(os.path.join(xdgdirs.XDG_CACHE_HOME, app_name))


DIR_PREFIX = os.path.abspath(
    os.path.dirname(os.path.dirname(sys.argv[0])))
    

DATA_DIR = os.path.join(DIR_PREFIX, 'share', app_name )
UI_DIR = os.path.join(DATA_DIR, 'ui')
ICON_DIR = os.path.join(DATA_DIR, 'icons')
LOCALE_DIR=os.path.join(DIR_PREFIX, 'share', 'locale')


WEB_URL = _meta.WEB_URL
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DJCGEPS4746PU'
TRANSLATIONS_URL = 'https://translations.launchpad.net/%s' % app_name
SOURCE_URL = 'https://code.launchpad.net/%s' % app_name
BUGREPORT_URL = 'https://bugs.launchpad.net/%s/+filebug' % app_name
QUESTION_URL = 'https://answers.launchpad.net/%s/+addquestion' % app_name


USER_APPLICATIONS_DIR = os.path.join(xdgdirs.XDG_DATA_HOME, 'applications/')
SYS_APPLICATIONS_DIR = '/usr/share/applications/'
USER_DESKTOP_DIR = xdgdirs.get_user_dir( 'desktop', '~/Desktop' )
USER_AUTOSTART_DIR = os.path.join(xdgdirs.XDG_CONFIG_HOME, 'autostart')

SYS_AUTOSTART_DIR = os.path.join('etc', 'xdg', 'autostart')
try:
    for dir in xdgdirs.XDG_CONFIG_DIRS.split(':'):
        path = os.path.join(dir, 'autostart')
        if os.path.isdir(path):
            SYS_AUTOSTART_DIR = path
            break
except:
    pass

DEFAULT_ICON='system-file-manager'
DEFAULT_ICON_SIZE = 64
DEFAULT_FILENAME = os.path.join(USER_DESKTOP_DIR, 'noname.desktop')
LAST_FILENAME = DEFAULT_FILENAME


KNOWN_DESKTOPS={'GNOME': _('GNOME Desktop'),
                'KDE': _('KDE Desktop'), 
                'LXDE': _('LXDE Desktop'),
                'LXQt':	_('LXQt Desktop'),
                'MATE': _('MATE Desktop'),
                'Razor': _('Razor-qt Desktop'),
                'ROX': _('ROX Desktop'),
                'TDE': _('Trinity Desktop'),
                'Unity': _('Unity Desktop'), 
                'XFCE': _('XFCE Desktop'),
                'EDE':	_('EDE Desktop'),
                'Cinnamon': _('Cinnamon Desktop'),
                'Pantheon': _('Pantheon Desktop'),
                'Old': _('Legacy menu systems')
            }

