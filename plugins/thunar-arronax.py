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


import gettext, locale, os.path, subprocess, logging

import gi
from gi.repository import GObject, Gio

gi.require_version("Thunarx", "3.0")
from gi.repository import Thunarx

GETTEXT_DOMAIN = 'arronax'

import sys

class Plugin(GObject.GObject,  Thunarx.MenuProvider):

    def __init__(self):
        GObject.GObject.__init__(self)
        locale_dir = self._get_locale_dir()
        print('Initializing Arronax from', __file__)
        locale_dir = self._get_locale_dir()
        locale.bindtextdomain(GETTEXT_DOMAIN, locale_dir)
        gettext.install(GETTEXT_DOMAIN, locale_dir)


    def _get_locale_dir(self):
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(__file__)))
        dir = os.path.join(base_dir, 'locale')
        locale_dir = gettext.find(GETTEXT_DOMAIN, dir)
        if not locale_dir:
            locale_dir = gettext.find(GETTEXT_DOMAIN)
        if locale_dir:
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
        
        menuitem = Thunarx.MenuItem(name='Arronax::FileMenu', label=label,
                             icon='arronax')
        menuitem.connect('activate', callback)
        
        return menuitem

    def _get_menuitemlabel(self, nfile, gfile, path):
    
        finfo = gfile.query_info(
            Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE,
            Gio.FileQueryInfoFlags.NONE,
            None)    # a Gio.FileInfo
      
        if path is not None and os.path.isdir(path):
            text =  _('Create a starter for this location')
        elif nfile.get_mime_type() == 'application/x-desktop':
            text = _('Modify this starter')
        elif finfo.get_attribute_boolean(
                Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE):
             text = _('Create a starter for this program')
        else:
            text = _('Create a starter for this file')

        logging.debug('menu item: p:"{}" yt:"{}"'.format(path, text))
        return text
        
    def get_file_menu_items(self, window, files):
        try:
            nfile = files[0]
        except IndexError:
            return

        gfile = nfile.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str
 
        text = self._get_menuitemlabel(nfile, gfile, path)
        return [self._create_menu_item(text, path=path)]
            

    def get_background_menu_items(self, window, file):
        gfile = file.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str
        
        text =  _('Create a starter')
        return [self._create_menu_item(text, basedir=path)]


