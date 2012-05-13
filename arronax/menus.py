#!/usr/bin/env python
#-*- coding: utf-8-*-


from gi.repository import Nautilus, GObject
import gettext, locale
from gettext import gettext as _

class ColumnExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        pass
        
    def get_file_items(self, window, files):
        top_menuitem = Nautilus.MenuItem(name='Arronax::FileMenu', 
                                         label=_('Create starter for this file'), 
                                         tip='',
                                         icon='')

        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        sub_menuitem = Nautilus.MenuItem(name='Arronax::FileSubMenu', 
                                         label='Bar', 
                                         tip='',
                                         icon='')
        submenu.append_item(sub_menuitem)

        return top_menuitem,

    def get_background_items(self, window, file):
        menuitem=Nautilus.MenuItem(name='Arronax::DesktopMenu', 
                                         label=_('Create starter'), 
                                         tip='',
                                         icon='')

        return menuitem,

    
