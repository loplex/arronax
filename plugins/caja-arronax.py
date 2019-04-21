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


class Plugin(GObject.GObject,  Caja.MenuProvider):

    def __init__(self):
        gettext.bindtextdomain(GETTEXT_DOMAIN)
        gettext.textdomain(GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(GETTEXT_DOMAIN, 'UTF-8')
        print('Initializing Arronax ...')

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
            text = _('Create a starter for this location')
        elif nfile.is_mime_type('application/x-desktop'):
            text = _('Modify this starter')
        elif finfo.get_attribute_boolean(
                Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE):
             text = _('Create a starter for this program')
        else:
            text = _('Create a starter for this file')

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

        text = _('Create a starter')
        return [self._create_menu_item(text, basedir=path)]


