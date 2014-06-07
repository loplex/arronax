#-*- coding: utf-8-*-

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib, urlparse
from gettext import gettext as _
import gettext

import settings

gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
gettext.textdomain(settings.GETTEXT_DOMAIN)
gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

FILE_DLG_DEF = {
    'dlg_open': {'title': _('Open File'),
                 'action':  Gtk.FileChooserAction.OPEN,
                 'patterns': ['*.desktop', '*'],
                 'buttons': [(_('Desktop'),
                              settings.USER_DESKTOP_DIR),
                             (_('User App Folder'),
                              settings.USER_APPLICATIONS_DIR),
                             (_('System App Folder'),
                              settings.SYS_APPLICATIONS_DIR),
                             ],
             },
    'dlg_save': {'title': _('Save File'),
             'action':  Gtk.FileChooserAction.SAVE,
             'buttons': [(_('Desktop'),
                          settings.USER_DESKTOP_DIR),
                         (_('User App Folder'),
                          settings.USER_APPLICATIONS_DIR),
                         ],
             },
    'dlg_working_dir': {'title': _('Select Folder'),
                     'action':  Gtk.FileChooserAction.SELECT_FOLDER,
                    },
    'dlg_command': {'title': _('Select Program'),
                'action':  Gtk.FileChooserAction.OPEN,
                },
    'dlg_file': {'title': _('Select File'),
             'action':  Gtk.FileChooserAction.OPEN,
                },
    }



def create_filechooser_dlg(title, action, patterns=None, mime_types=None):
    dlg = Gtk.FileChooserDialog(title, None, action, 
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK, Gtk.ResponseType.OK))
    if patterns is not None:
        for p in patterns:
            filter = Gtk.FileFilter()
            filter.add_pattern(p)
            filter.set_name(p)
            dlg.add_filter(filter)
    if mime_types is not None:
        for m in mime_types:
            filter = Gtk.FileFilter()
            filter.add_mime_type(m)
            filter.set_name(m)
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




def ask_for_filename(defname, add_ext=False, default=None):
    dlgdef = FILE_DLG_DEF[defname]
    dialog = create_dir_buttons_filechooser_dlg(
        title=dlgdef['title'],
        action=dlgdef['action'],
        patterns=dlgdef.get('patterns', None),
        mime_types=dlgdef.get('mime_types', None),
        dir_buttons=dlgdef.get('buttons', None)
    )

    is_save_action = (dlgdef['action'] in 
                      (Gtk.FileChooserAction.SAVE,
                       Gtk.FileChooserAction.CREATE_FOLDER))
    if default is not None:
        if os.path.isdir(default) or default=='':
            folder = default
        else:
            folder = os.path.dirname(default)
        if folder == '':
            folder = settings.USER_DESKTOP_DIR   
        dialog.set_current_folder(folder)

        file = os.path.basename(default)
        if file != '':
            if is_save_action:
                dialog.set_current_name(file)
            else:
                dialog.select_filename(default)

    response = dialog.run()
    path = dialog.get_filename()
    dialog.destroy()
    if response != Gtk.ResponseType.OK:
        return
    if (add_ext and 
        not path.endswith('.desktop') and 
        not os.path.isfile(path)):
        path='%s.desktop' % path
    return path

    
