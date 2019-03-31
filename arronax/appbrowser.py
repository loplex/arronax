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
#

import os.path
from gi.repository import Gtk, GdkPixbuf, Gio

from arronax import settings, entrytools

class AppBrowser():
    def __init__(self, parent):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
      
        self.builder.add_from_file(
            os.path.join(settings.UI_DIR, "appbrowser.ui"))
        self.builder.connect_signals(self)
        entrytools.add_clear_button_to_builder_obj(self.builder)
        self.tv = self['tv']
        self.filter = ''

        self['dialog'].set_transient_for(parent)
        
        self.create_list()        
        
    def __getitem__(self, key):
        return self.builder.get_object(key)
    
    def run(self, default):
        dlg = self['dialog']
        dlg.show()
        self.fill_list(default)
        answer = dlg.run()
        aid = None
        path, column = self.tv.get_cursor()
        if answer == Gtk.ResponseType.OK and path is not None:
            model = self.tv.get_model()
            aid = model[path][2]
        dlg.destroy()
        return aid

        
    def create_list(self):
        model = liststore = Gtk.ListStore(Gio.Icon, str, str)
        fmodel = model.filter_new(None)
        
        def visifunc(model, iter, data):
            if model[iter]:
                name = model[iter][1].lower()
                aid =  model[iter][2].lower()
                return (self.filter == '' or
                        self.filter.lower() in name or
                        self.filter.lower() in aid 
                            )
            else:
                return True
        fmodel.set_visible_func(visifunc)

        
        self.icon_col = Gtk.TreeViewColumn('Application')
        self.icon_col.set_spacing(3)
        
        self.tv.append_column(self.icon_col)
        self.cell = Gtk.CellRendererPixbuf()
        self.icon_col.pack_start(self.cell, False)
        self.icon_col.add_attribute(self.cell, 'gicon', 0)

        self.cell = Gtk.CellRendererText()
        self.icon_col.pack_start(self.cell, False)
        self.icon_col.add_attribute(self.cell, 'text', 2)


        self.cell = Gtk.CellRendererText()
        self.icon_col.pack_start(self.cell, True)
        self.icon_col.add_attribute(self.cell, 'text', 1)


        self.tv.set_model(fmodel)

    def fill_list(self, current):
        self['swin'].hide()
        self['box_filter'].hide()
        model = self.tv.get_model().get_model()
        self.tv.freeze_notify()
        for appinfo in sorted(Gio.app_info_get_all(),
                                  key=lambda x: x.get_id()):
            aiter = model.append([appinfo.get_icon(),
                                appinfo.get_name(),
                                appinfo.get_id()])
            if appinfo.get_id() == current:
                tpath = model.get_path(aiter)
                self.tv.set_cursor(tpath)
        self.tv.thaw_notify()
        self['swin'].show()
        self['box_filter'].show()

   
    def on_e_filter_changed(self, *args):
        self.filter = self['e_filter'].get_text()
        self.tv.get_model().refilter()

