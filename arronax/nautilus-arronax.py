#!/usr/bin/env python
#-*- coding: utf-8-*-


from gi.repository import Nautilus, GObject
import gettext, locale
from gettext import gettext as _

from arronax import editor

class ColumnExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        print 'Initializing Arronax...'


    def open_editor(self, path=None):
        ed = editor.Editor(path)
        

    def get_file_items(self, window, files):
        menuitem = Nautilus.MenuItem(name='Arronax::FileMenu', 
                                         label=_('Create starter for this file'), 
                                         tip='',
                                         icon='')

        menuitem.connect('activate', lambda *x: self.open_editor())
        return menuitem,

    def get_background_items(self, window, file):
        menuitem=Nautilus.MenuItem(name='Arronax::DesktopMenu', 
                                         label=_('Create starter'), 
                                         tip='',
                                         icon='')
        menuitem.connect('activate', lambda *x: self.open_editor())
        return menuitem,





    
