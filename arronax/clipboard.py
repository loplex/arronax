#-*- coding: utf-8-*-
#
# Unsettings - a configuration frontend for the Unity desktop environment
#
# Copyright (C) 2012 Florian Diesch <devel@florian-diesch.de>
#
# Homepage: http://www.florian-diesch.de/software/unsettings/
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


from gi.repository import Gtk, Gdk

class ContainerClipboard(object):
    def __init__(self, container, builder=None):
        self.container = container
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        if builder:
            self.add_actions_from_builder(builder)

    def _get_focus_widget(self, container=None):
        if container is None:
            container = self.container
        focus = container.get_focus_child()
        if focus is None or (focus.is_focus()):
            return focus
        else:
            return self._get_focus_widget(focus)

    
    def add_actions(self, cut=None, copy=None, paste=None, delete=None):
        if cut is not None:
            cut.connect('activate', lambda *args: self.cut())
        if copy is not None:
            copy.connect('activate', lambda *args: self.copy())
        if paste is not None:
            paste.connect('activate', lambda *args: self.paste())
        if delete is not None:
            delete.connect('activate', lambda *args: self.delete())

    def add_actions_from_builder(self, builder):
        self.add_actions(builder.get_object('ac_cut'),
                         builder.get_object('ac_copy'),
                         builder.get_object('ac_paste'),
                         builder.get_object('ac_delete'))


    def cut(self):
        widget = self._get_focus_widget()
        if isinstance(widget, Gtk.Editable):
            widget.cut_clipboard()
        elif isinstance(widget, Gtk.TextView):
            buffer = widget.get_buffer()
            if buffer is not None:
                buffer.cut_clipboard(self.clipboard, True)

    def copy(self):
        widget = self._get_focus_widget()
        if isinstance(widget, Gtk.Editable):
            widget.copy_clipboard()
        elif isinstance(widget, Gtk.TextView):
            buffer = widget.get_buffer()
            if buffer is not None:
                buffer.copy_clipboard(self.clipboard)
            
    def paste(self):
        widget = self._get_focus_widget()
        if isinstance(widget, Gtk.Editable):
            widget.paste_clipboard()
        elif isinstance(widget, Gtk.TextView):
            buffer = widget.get_buffer()
            if buffer is not None:
                buffer.paste_clipboard(self.clipboard, None, True)

    def delete(self):
        widget = self._get_focus_widget()
        if isinstance(widget, Gtk.Editable):
            widget.delete_selection()
        elif isinstance(widget, Gtk.TextView):
            buffer = widget.get_buffer()
            if buffer is not None:
                buffer.delete_selection(True, True)
                     
         
    
