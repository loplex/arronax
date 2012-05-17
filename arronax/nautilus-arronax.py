#!/usr/bin/env python
#-*- coding: utf-8-*-


from gi.repository import Nautilus, GObject
import gettext, locale
from gettext import gettext as _

from arronax import editor

class ColumnExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        print 'Initializing Arronax...'


    def open_editor(self, desktop_path=None, command=None):
        ed = editor.Editor(desktop_path, command)
        

    def get_file_items(self, window, files):
        try:
            nfile = files[0]
        except IndexError:
            return
        path = nfile.get_location().get_path()
        menuitem = Nautilus.MenuItem(name='Arronax::FileMenu', 
                                         label=_('Create starter for this file'), 
                                         tip='',
                                         icon='')

        dfile = cmd = None
        if nfile.is_mime_type('application/x-desktop') or nfile.is_directory():
            dfile = path
        else:
            cmd = path
        menuitem.connect('activate', lambda *x: self.open_editor(dfile, cmd))
        return menuitem,

    def get_background_items(self, window, file):
        menuitem=Nautilus.MenuItem(name='Arronax::DesktopMenu', 
                                         label=_('Create starter'), 
                                         tip='',
                                         icon='')
        menuitem.connect('activate', lambda *x: self.open_editor())
        return menuitem,





    
