# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib, urlparse
import settings, statusbar

def activate_drag_and_drop(widget, callback=None, field=None):
    if callback is not None:
        widget.connect('drag-data-received', callback, field)

    widget.drag_dest_set(Gtk.DestDefaults.ALL, [],  
                         Gdk.DragAction.COPY)
    widget.drag_dest_add_uri_targets()
    widget.drag_dest_add_text_targets()


def create_toggle_renderer(treeview):
    def toggle_value(widget, path):
        model = treeview.get_model()
        if model is None:
            return
        _iter = model.get_iter(path)
        model[_iter][0] = not model[_iter][0]

    renderer = Gtk.CellRendererToggle()
    renderer.connect('toggled', toggle_value)
    return renderer

def get_desktops_from_tv(tv):    
    model = tv.get_model()
    if all(row[0] for row in model):
        return ''
    else:
        ds = [row[2] for row in model if row[0]]
        result = ';'.join(ds)        
        return result + ';'
                                
def load_desktops_into_tv(tv, desktops):
    model = tv.get_model()
    ds = set(i.strip() for i in desktops.split(';') if i.strip() != '')
    for row in model:
        row[0] = row[2] in ds
    if not any(row[0] for row in model):
        for row in model:
            row[0] = True

def get_quicklist_from_tv(tv):
    model = tv.get_model()
    return [(row[0], row[1], row[2]) for row in model]
    
def load_quicklist_into_tv(tv, qlist):
    model = tv.get_model()
    model.clear()
    for row in qlist:
        model.append(row)

def get_mime_types_from_uris(uris, error_func=None):
    result = set()
    for uri in uris:
        try:
            gfile = Gio.File.new_for_uri(uri)
            info = gfile.query_info("standard::*", 
                                    Gio.FileQueryInfoFlags.NONE, None)
            result.add(info.get_content_type())
        except GLib.GError as e:
            if error_func:
                error_func(e)
    return result

def get_name_from_image(img):
    stype = img.get_storage_type()
    if stype == Gtk.ImageType.PIXBUF:
        return img.get_pixbuf().__arronax_filename
    elif stype ==  Gtk.ImageType.ICON_NAME:
        return img.get_icon_name()[0]
    elif stype ==  Gtk.ImageType.EMPTY:
        return ''
    else:
        return '???'

    
def load_file_into_image(img, path):
    try:
        if '/' not in path:
            img.set_from_icon_name(path, settings.DEFAULT_ICON_SIZE)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, 
                settings.DEFAULT_ICON_SIZE,
                settings.DEFAULT_ICON_SIZE)
            pixbuf.__arronax_filename = path
            if pixbuf is not None:
                img.set_from_pixbuf(pixbuf)
    except Exception as e:
        print e
        return str(e)


def make_keyfile_list_string(alist):
    result = ';'.join(alist)   
    return result

def get_list_from_textview(textview):
    buffer = textview.get_buffer()
    content = buffer.get_text(buffer.get_start_iter(),
                              buffer.get_end_iter(), False)    
    result = [x for x in content.splitlines() if x.strip() != '']
    return result

def set_list_to_textview(textview, alist):
    if isinstance(alist, str):
        alist = [i for i in alist.split(';') if i.strip() != '']
    buffer = textview.get_buffer()
    buffer.set_text('\n'.join(alist))



def get_field_from_desktop_file(path, field):   
    keyfile = GLib.KeyFile()
    try:
        keyfile.load_from_file(path,
                               GLib.KeyFileFlags.KEEP_COMMENTS | 
                               GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        return keyfile.get_string('Desktop Entry', field)
    except Exception as e:
        print 'GET FIELD:', path, e
        return ''


def get_path_for_application_uri(uri):
    appinfo = Gio.DesktopAppInfo.new(uri.netloc)
    return appinfo.get_filename()

def get_mime_type(uri):
    try:
        gfile = Gio.File.new_for_uri(uri.geturl())
        info = gfile.query_info("standard::*", 
                                Gio.FileQueryInfoFlags.NONE, None)
        return info.get_content_type()
    except Exception as e:
        print 'GET MIME:', e
        return ''
    
def is_desktop_file(uri):
    try:
        gfile = Gio.File.new_for_uri(uri)
        info = gfile.query_info("standard::*", 
                                Gio.FileQueryInfoFlags.NONE, None)
        return info.get_content_type() == 'application/x-desktop'
    except Exception as e:
        print('IS_DESKTOP_FILE:', e)
        return False

def get_info_from_uri(uri_string, desktop_field=None):
    result = ''
    uri = urlparse.urlparse(uri_string)
    if uri.scheme == 'application':
        try:
            path = get_path_for_application_uri(uri)
            result = get_field_from_desktop_file(path, desktop_field)
        except Exception as e:
            result = uri.netloc
    elif uri.scheme == 'file':                
        if is_desktop_file(uri.geturl()):
            if desktop_field:
                result = get_field_from_desktop_file(
                    uri.path, desktop_field)
    if result == '':
        try:
            gfile = Gio.File.new_for_uri(uris[0])
            ginfo = gfile.query_info("standard::*", 
                                     Gio.FileQueryInfoFlags.NONE, None)
            result = ginfo.get_display_name()
        except:
            result = uri.path
    return result
