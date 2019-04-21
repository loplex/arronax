#!/usr/bin/env python
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


from gi.repository import Gtk
import gettext, locale
from gettext import gettext as _





def yes_no_question(parent, title, text):    
    dlg = Gtk.MessageDialog(parent, 0,  Gtk.MessageType.QUESTION,
                            Gtk.ButtonsType.NONE,
                            text
                            )
    dlg.set_title(title)
    dlg.add_buttons(
        Gtk.STOCK_YES, Gtk.ResponseType.YES,
        Gtk.STOCK_NO, Gtk.ResponseType.NO,
        )
    result = dlg.run()
    dlg.destroy()
    return result

def yes_no_cancel_question(parent, title, text):    
    dlg = Gtk.MessageDialog(parent, 0,  Gtk.MessageType.QUESTION,
                            Gtk.ButtonsType.NONE,
                            text
                            )
    dlg.set_title(title)
    dlg.add_buttons(
        Gtk.STOCK_YES, Gtk.ResponseType.YES,
        Gtk.STOCK_NO, Gtk.ResponseType.NO,
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,                    
        )
    result = dlg.run()
    dlg.destroy()
    return result

def information(parent, title, text):    
    dlg = Gtk.MessageDialog(parent, 0,  Gtk.MessageType.INFO,
                            Gtk.ButtonsType.OK,
                            text
                            )
    dlg.set_title(title)
    result = dlg.run()
    dlg.destroy()
    return result   
 
def error(parent, title, text):    
    dlg = Gtk.MessageDialog(parent, 0,  Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            text
                            )
    dlg.set_title(title)
    result = dlg.run()
    dlg.destroy()
    return result    
