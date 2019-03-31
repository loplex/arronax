#-*- coding: utf-8-*-

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib.request, urllib.parse, urllib.error, urllib.parse
from gettext import gettext as _
import gettext

from . import settings

gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
gettext.textdomain(settings.GETTEXT_DOMAIN)
gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

FILE_DLG_DEF = {
    'dlg_open': {'title': _('Open File'),
                 'action':  Gtk.FileChooserAction.OPEN,
                 'patterns': ['*.desktop', '*'],
             },
    'dlg_save': {'title': _('Save File'),
             'action':  Gtk.FileChooserAction.SAVE,
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
    label = Gtk.Label(_('Standard folders: '))
    box = Gtk.HBox()
    box.add(label)
    cbox = Gtk.ComboBox()
    renderer = Gtk.CellRendererText()
    cbox.pack_start(renderer, True)
    cbox.add_attribute(renderer, "text", 0)
    model = Gtk.ListStore(str, str)
    model.append((_('Desktop'), settings.USER_DESKTOP_DIR))
    model.append((_('User App Folder'), settings.USER_APPLICATIONS_DIR))
    model.append((_('System App Folder'), settings.SYS_APPLICATIONS_DIR))
    model.append((_('User Autostart Folder'), settings.USER_AUTOSTART_DIR))
    model.append((_('System Autostart Folder'), settings.SYS_AUTOSTART_DIR))

    cbox.set_model(model)
    box.add(cbox)

    def callback(*args):
        i = cbox.get_active()
        name, path = model[i]
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as e:
                print(e)
        dlg.set_current_folder(path)

    cbox.connect('changed', callback)

    box.show_all()
    dlg.set_extra_widget(box)
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
    if response != Gtk.ResponseType.OK or path is None:
        return
    if (add_ext and 
        not path.endswith('.desktop') and 
        not os.path.isfile(path)):
        path='%s.desktop' % path
    return path

    
