#-*- coding: utf-8-*-

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib, urlparse
from gettext import gettext as _
import gettext

def create_filechooser_dlg(title, action, patterns=None, mime_types=None):
    dlg = Gtk.FileChooserDialog(title, None, action, 
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK, Gtk.ResponseType.OK))
    if patterns is not None:
        for p in patterns:
            filter = Gtk.FileFilter()
            filter.add_pattern(p)
            dlg.add_filter(filter)
    if mime_types is not None:
        for m in mime_types:
            filter = Gtk.FileFilter()
            filter.add_mime_type(m)
            dlg.add_filter(filter)
    return dlg



def create_dir_buttons_filechooser_dlg(title, action, 
                                       patterns=None,
                                       mime_types=None,
                                       dir_buttons=None):
    dlg = create_filechooser_dlg(title, action, patterns, mime_types)
    if dir_buttons is not None:
        bbox = Gtk.HButtonBox()
        for title, dir in dir_buttons:
            def callback(widget, dir=dir, title=title, dlg=dlg):
                if not os.path.isdir(dir):
                    try:
                        os.makedirs(dir)
                    except Exception, e:
                        print e
                        return
                dlg.set_current_folder(dir)
            bt = Gtk.Button.new_with_label(title)
            bt.connect('clicked', callback)
            bbox.pack_end(bt, False, True, 6)
        bbox.show_all()
        dlg.set_extra_widget(bbox)
    return dlg



    
