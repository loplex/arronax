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

import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Gdk, Wnck

from gettext import gettext as _

from . import dialogs

class WindowClassSelector:

    def __init__(self, parent, dest_widget):
        self.parent = parent
        self.dest_widget = dest_widget
        
    def create_window(self):
        window = Gtk.Window()
        window.set_transient_for(self.parent)    
        window.set_default_size(100, 100)
        window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        window.set_modal(True)
        window.set_border_width(12)
        
        label = Gtk.Label.new(_('Click a window to get its window class'))

        window.add(label)
        window.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration()
        return window
    
    def have_X11(self):
        seat = self.get_default_seat()
        pointer = seat.get_pointer()
        screen, x, y = pointer.get_position()
        screen = Wnck.Screen.get_default()
        return screen != None
        
    def get_default_seat(self):
        display = Gdk.Display.get_default()
        return display.get_default_seat()

    def show_X11_error(self):
        msg = _("This function needs a X11 session. "
                "It doesn't work with Wayland.")
        dialogs.error(self.parent, _('Error'), msg)
        
    def get_window_class_at_pointer(self):
        seat = self.get_default_seat()
        pointer = seat.get_pointer()
        screen, x, y = pointer.get_position()
        screen = Wnck.Screen.get_default()
        if screen is None:
            self.show_X11_error()
            return
        screen.force_update()
        wspace = screen.get_active_workspace()
        windows = screen.get_windows_stacked()
        for w in windows[::-1]:
            wx, wy, wdx, wdy = w.get_geometry()
            if (w.is_on_workspace(wspace) and
                wx <=x <= wx+wdx and wy <= y <= wy+wdy):
                return  w.get_class_instance_name()
        return ''
    

    def run(self):
        if not self.have_X11():
            self.show_X11_error()
            return
        window = self.create_window()
        win = window.get_window()
        cursor = Gdk.Cursor(Gdk.CursorType.HAND1)    
        seat = self.get_default_seat()

        def callback(*args):
            try:
                wclass = self.get_window_class_at_pointer()
                if wclass is not None:
                    self.dest_widget.set_text(wclass)
            finally:
                seat.ungrab()
                window.destroy()

        window.connect('button-press-event', callback)

        seat.grab(window=win,
                  capabilities=Gdk.SeatCapabilities.ALL_POINTING,
                  owner_events = True,
                  cursor = cursor,
                  event = None,
                  prepare_func = None,
                  prepare_func_data = None
                  )
        


