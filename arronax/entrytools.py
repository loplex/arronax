# -*- coding: utf-8 -*-
# Fernweh - Put things on a map
# https://florian-diesch.de/software/fernweh/
#
# Copyright (C) 2017 Florian Diesch devel@florian-diesch.de
#
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



def add_clear_button(entry):
    entry.set_icon_from_icon_name(
        Gtk.EntryIconPosition.SECONDARY, 'gtk-clear')
    entry.set_icon_sensitive(
        Gtk.EntryIconPosition.SECONDARY, True)
    entry.connect('icon_press', lambda e, *args: e.set_text(''))

def add_clear_button_to_builder_obj(builder):
    for obj in builder.get_objects():
        if isinstance(obj, Gtk.Entry):
           add_clear_button(obj) 
