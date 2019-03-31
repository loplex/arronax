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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, GObject
import os, os.path, time, sys, urllib.request, urllib.parse, urllib.error, urllib.parse
from gettext import gettext as _

from . import tvtools, settings, entrytools

class Quicklist(object):

    def __init__(self, parent, treeview):
        self.parent = parent
        self.tv = treeview
        self.setup_treeview()

    def setup_treeview(self):
        model = Gtk.ListStore(str, str, str)
        self.tv.set_model(model)
        tvtools.create_treeview_column(self.tv, _('Title'), 0)

        ## dropping files here shouln'd be handled by the window
        self.tv.drag_dest_add_uri_targets() 

    def create_edit_dialog(self, title, command):
        builder = Gtk.Builder()
        builder.set_translation_domain(settings.GETTEXT_DOMAIN)
        builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'quicklist.ui'))
        
        entrytools.add_clear_button_to_builder_obj(builder)
        e_title = builder.get_object('e_title')
        e_title.set_text(title)

        e_command = builder.get_object('e_command')
        e_command.set_text(command)

        dialog = builder.get_object('dialog')
        dialog.set_transient_for(self.parent)

        dialog.connect('drag-data-received', 
                       self.on_drag_data_received, e_title, e_command)
        dialog.drag_dest_set(Gtk.DestDefaults.ALL, [],  
                               Gdk.DragAction.COPY)
        dialog.drag_dest_add_uri_targets()

        return dialog, e_title, e_command

    def get_current_row(self):
        try:
            title, command, group =  tvtools.get_current_row(self.tv)
        except TypeError: # not row selected
            title = command = group = ''
        return title, command, group

    def goto_next_row(self):
         tvtools.move_current_row_down(self.tv)

    def goto_prev_row(self):
         tvtools.move_current_row_up(self.tv)
   
    def remove_current_row(self):
        tvtools.del_current_row(self.tv)

    def edit_current_row(self):
        title, command, group = self.get_current_row()
        try:
            title, command = self.edit_item(title, command)
            tvtools.set_current_row(self.tv, [title, command, group])
        except TypeError:  # cancel button pressed
            pass

    def new_row(self):
        try:
            title, command = self.edit_item('', '')
            tvtools.insert_row_after_current(self.tv, [title, command, ''])
        except TypeError:  # cancel button pressed
            pass

    def duplicate_current_row(self):
        title, command, _ = self.get_current_row()
        tvtools.insert_row_after_current(self.tv, [title, command, ''])

    def edit_item(self, title, command):
        dialog, e_title, e_command = self.create_edit_dialog(title, command)

        response = dialog.run()
        title = e_title.get_text()
        command = e_command.get_text()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            return title, command
        else:
            return None

    def get_row_from_drag_and_drop(self, uris, info):
        if info == 0 and len(uris) > 0:            
            uri = urllib.parse.urlparse(uris[0])
            filename = None
            if uri.scheme == 'file':
                gfile = Gio.File.new_for_uri(uris[0])
                ginfo = gfile.query_info("standard::*", 
                                        Gio.FileQueryInfoFlags.NONE, None)
                mimetype = ginfo.get_content_type()
                filename = urllib.request.url2pathname(uri.path)
                title = ginfo.get_display_name()
            elif uri.scheme == 'application':
                appinfo = Gio.DesktopAppInfo.new(uri.netloc)
                filename = appinfo.get_filename()
                mimetype = 'application/x-desktop'
                title = '' # handled by get_row_from_desktop_fil
            if filename:
                if mimetype == 'application/x-desktop':
                    row = self.get_row_from_desktop_file(filename)
                    return row
                else:
                    return title, filename, ''

    def get_row_from_desktop_file(self, path):
        keyfile = GLib.KeyFile()
        try:
            keyfile.load_from_file(path,
                                   GLib.KeyFileFlags.KEEP_COMMENTS | 
                                   GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except Exception as e:
            print(str(e))
        group = 'Desktop Entry'
        title = keyfile.get_string(group, 'Name')
        command = keyfile.get_string(group, 'Exec')
        return title, command, ''
        
    def on_drag_data_received(self, widget, drag_context, x, y,
                              data, info, time, 
                              e_title, e_command):        
        uris = data.get_uris()
        title, command, _ = self.get_row_from_drag_and_drop(uris, info)
        e_title.set_text(title)
        e_command.set_text(command)
