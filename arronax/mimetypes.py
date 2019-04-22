#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, GObject, Pango
import os, os.path
from gettext import gettext as _
from . import  settings, tvtools, utils, entrytools


class MimetypesDlg:

    def __init__(self, mime_types):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                "mimetypes.ui"))
        self.builder.connect_signals(self)
        entrytools.add_clear_button_to_builder_obj(self.builder)
        
        self.mime_types = set(mime_types)
        self.filter = ''
        self.setup_tv()
        utils.activate_drag_and_drop(self['dialog1'])
        
    def setup_tv(self):
        tv = self['tv_mimetypes']
        def func(model, column, key, iter, *search_data):
            value = model[iter][column]
            return key not in value
        tv.set_search_equal_func(func, None, None)
        model = Gtk.ListStore(bool, str, str)
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        fmodel = model.filter_new(None)
        
        def visifunc(model, iter, data):
            if model[iter]:
                name = model[iter][1].lower()
                desc =  model[iter][2].lower()
                return (self.filter == '' or
                        self.filter.lower() in name or
                        self.filter.lower() in desc
                            )
            else:
                return True
        fmodel.set_visible_func(visifunc)

        tv.set_model(fmodel)
        tvtools.create_treeview_column(
            tv, _('Selected'), 0,
            utils.create_toggle_renderer(tv),
            activatable=True,
            attr='active', 
        )
        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        renderer.set_property('ellipsize-set', True)
        renderer.set_property('max-width-chars', 30)
        col, ren = tvtools.create_treeview_column(
            tv, _('Name'), 1, renderer=renderer, min_width=200)
        col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvtools.create_treeview_column(
            tv, _('Description'), 2)
        for name, desc in sorted(self.get_all_mime_types()):
            model.append([name in self.mime_types, name, desc])


    def get_all_mime_types(self):
        result = []
        for mt in Gio.content_types_get_registered():
            desc = Gio.content_type_get_description(mt)
            result.append((mt, desc))
        return result
            
    def __getitem__(self, key):
        return self.builder.get_object(key)

    def run(self):
        Gtk.main()
        
    def quit(self):
        Gtk.main_quit()

    def run(self):
        dlg = self['dialog1']
        response = dlg.run()
        model = self['tv_mimetypes'].get_model()
        mime_types = [name for (enabled, name, desc) in model if enabled]
        dlg.destroy()
        if response == Gtk.ResponseType.OK:
            return mime_types
        else:
            return None
        
    def show_msg(self, msg):
        statusbar = self['statusbar']
        context = statusbar.get_context_id('')
        if msg is not None:
            msg = str(msg)
            statusbar.push(context, msg)
            GLib.timeout_add(
                3000, 
                lambda *args: statusbar.pop(context))

    def on_dialog1_drag_data_received(self, widget, 
                                      drag_context, x, y, data,
                                      info, time):
        uris = data.get_uris()
        mime_types = utils.get_mime_types_from_uris(
            uris, self.show_msg)
        model = self['tv_mimetypes'].get_model()
        current = dict((row[1], row) for row in model)
        for mt in mime_types:
            row = current.get(mt, None)
            if row:
                row[0] = True
            else: 
                desc = Gio.content_type_get_description(mt)
                model.append((True, mt, desc))
            
    def on_e_filter_changed(self, *args):
        self.filter = self['e_filter'].get_text()
        self['tv_mimetypes'].get_model().refilter()
    
        
        
