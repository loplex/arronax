# -*- coding: utf-8 -*-
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


import gettext, os.path , subprocess, logging
from gettext import gettext as _

import gi
from gi.repository import GObject, Gio

gi.require_version('Caja', '2.0')
from gi.repository import Caja

GETTEXT_DOMAIN = 'arronax'

import sys
print('VERS:',  sys.version_info)

class Plugin(GObject.GObject,  Caja.MenuProvider):

    def __init__(self):
        print('Initializing Arronax from', __file__)
        try:
            t = gettext.translation(GETTEXT_DOMAIN, self._get_locale_dir())
            _ = t.gettext
        except Exception:
            _ = lambda x: x
        self.msg_create = _('Create a starter')
        self.msg_location =  _('Create a starter for this location')
        self.msg_modify = _('Modify this starter')
        self.msg_program =  _('Create a starter for this program')
        self.msg_file = _('Create a starter for this file')


    def _get_locale_dir(self):
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(__file__)))
        dir = os.path.join(base_dir, 'locale')
        locale_dir = gettext.find(GETTEXT_DOMAIN, dir)
        if not locale_dir:
            locale_dir = gettext.find(GETTEXT_DOMAIN)
        for i in range(3):
            locale_dir = os.path.dirname(locale_dir)
        return locale_dir
        
    def _create_menu_item(self, label, path=None, basedir=None):
        def callback(*args):
            cmd = ['arronax']
            if basedir is not None:
                cmd.extend(['--dir', basedir])
            if path is not None:
               cmd.append(path) 
            logging.info('Calling Arronax :{}'.format(cmd))
            subprocess.Popen(cmd)
        
        menuitem = Caja.MenuItem(name='Arronax::FileMenu', label=label,
                            tip='', icon='')
        menuitem.connect('activate', callback)
        
        return menuitem

    def _get_menuitemlabel(self, nfile, gfile, path):
    
        finfo = gfile.query_info(
            Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE,
            Gio.FileQueryInfoFlags.NONE,
            None)    # a Gio.FileInfo
        
        if os.path.isdir(path):
            text = self.msg_location
        elif nfile.is_mime_type('application/x-desktop'):
            text = self.msg_modify
        elif finfo.get_attribute_boolean(
                Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE):
             text = self.msg_program
        else:
            text = self.msg_file

        logging.debug('menu item: p:"{}" yt:"{}"'.format(path, text))
        return text
        
    def get_file_items(self, window, files):
        try:
            nfile = files[0]
        except IndexError:
            return

        gfile = nfile.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str
 
        text = self._get_menuitemlabel(nfile, gfile, path)
        return [self._create_menu_item(text, path=path)]
            
   

    def get_background_items(self, window, file):
        gfile = file.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str

        text = self.msg_create
        return [self._create_menu_item(text, basedir=path)]


