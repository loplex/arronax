#!/usr/bin/env python
#-*- coding: utf-8-*-


import gi
gi.require_version('Nautilus', '3.0')
 
from gi.repository import Nautilus, GObject, Gio
import gettext
from gettext import gettext as _
from arronax import editor, settings
import os.path


class ArronaxExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
        gettext.textdomain(settings.GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')
        print 'Initializing Arronax v%s...' % settings.APP_VERSION 



    def _create_starter_for(self, path):
        label = _('Create a starter for this program')
        func =  lambda *x: editor.Editor(path=path, 
                                         mode=editor.MODE_CREATE_FOR)
        return label, func

    def _create_starter_edit(self, path):
        label = _('Modify this starter')
        func =  lambda *x: editor.Editor(path=path, 
                                         mode=editor.MODE_EDIT)
        return label, func

    def _create_starter_in(self, path):
        label = _('Create a starter')
        func =  lambda *x: editor.Editor(path=path, 
                                         mode=editor.MODE_CREATE_IN)
        return label, func


    def _create_starter_link(self, path):
        label = _('Create a starter for this file')
        func =  lambda *x: editor.Editor(path=path, 
                                         mode=editor.MODE_CREATE_FOR,
                                         type=editor.TYPE_LINK)
        return label, func

    def _create_menu_item(self, label, func):
        menuitem = Nautilus.MenuItem(name='Arronax::FileMenu', 
                                         label=label, 
                                         tip='',
                                         icon='')

        menuitem.connect('activate', func)
        return menuitem

    def get_file_items(self, window, files):
        try:
            nfile = files[0]
        except IndexError:
            return

        gfile = nfile.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str
        finfo = gfile.query_info(Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE,
                                 Gio.FileQueryInfoFlags.NONE,
                                 None)    # a Gio.FileInfo

        if os.path.isdir(path):
            label, func = self._create_starter_link(path)
        elif nfile.is_mime_type('application/x-desktop'):
            label, func = self._create_starter_edit(path)
        elif finfo.get_attribute_boolean(Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE):
            label, func = self._create_starter_for(path)
        else:
            label, func = self._create_starter_link(path)

        return self._create_menu_item(label, func),


    def get_background_items(self, window, file):
        gfile = file.get_location()  # a Gio.GFile 
        path = gfile.get_path()       # a str

        label, func = self._create_starter_in(path)
        return self._create_menu_item(label, func), 
