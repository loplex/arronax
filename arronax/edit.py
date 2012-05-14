#!/usr/bin/env python
#-*- coding: utf-8-*-

from gi.repository import Gtk, GdkPixbuf, GLib
import os, os.path, time, sys
from gettext import gettext as _

import settings, connection, desktopfile, widgets, clipboard

IS_STANDALONE = False


class Editor(object):

    def __init__(self, file=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'edit.ui'))
        self.builder.connect_signals(self)
        
        self.win = self.obj('window1')

        self.clip = clipboard.ContainerClipboard(self.obj('box_main'))
        self.clip.add_actions(cut=self.obj('ac_cut'),
                              copy=self.obj('ac_copy'),
                              paste=self.obj('ac_paste'),
                              delete=self.obj('ac_delete'))

        self.dfile = desktopfile.DesktopFile(self.win, file)
        self.factory = widgets.WidgetFactory(self.builder)

        self.obj('img_icon').set_from_file(settings.DEFAULT_ICON)

        self.conn = connection.ConnectionGroup(self.dfile)
        self.conn.add('Name', self.factory.get('e_title'))
        self.conn.add('Comment', self.factory.get('e_comment'))
        self.conn.add('Exec', self.factory.get('e_command'))
        self.conn.add('Hidden', self.factory.get('sw_hidden'))
        self.conn.add('Terminal', self.factory.get('sw_run_in_terminal'))
        self.conn.add('Icon', self.factory.get('img_icon'))
        self.conn.add('Path', self.factory.get('e_working_dir'))
        
        self.conn.view()

        if file is not None:            
            self.obj('e_filename').set_text(file)
            if self.obj('e_title').get_text() == '' and os.path.isfile(file):
                title = os.path.basename(file)
                if title.endswith('.desktop'):
                    title=title[:-len('.desktop')]
                self.obj('e_title').set_text(title.title())

        self.win.show()


    def obj(self, name):
        return self.builder.get_object(name)

    def quit(self):
        if IS_STANDALONE:
            Gtk.main_quit()
        else:
            self.win.destroy()


    def select_icon(self):
        preview = Gtk.Image()

        dialog = Gtk.FileChooserDialog(_("Select Icon"), self.win,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, 
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, 
                                        Gtk.ResponseType.OK))
        dialog.set_preview_widget(preview)
        dialog.set_use_preview_label(False)
        dialog.set_filename(settings.LAST_ICON)

        def update_preview(widget, *args):
            path = widget.get_preview_filename()
            if path is None or not os.path.isfile(path):
                return
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
            except GLib.GError, e:
                print e
                return
            
            preview.set_from_pixbuf(pixbuf)
            widget.set_preview_widget_active(True);

        dialog.connect("update-preview", update_preview)

        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        
        if response != Gtk.ResponseType.OK:
            return
        
        self.set_icon(path)

    def set_icon(self, path):
        settings.LAST_ICON = path
        print path
        self.obj('img_icon').set_from_file(path)



#####################
## signal handlers
#####################

###############
## main window

    def on_window1_delete_event(self, *args):
        self.quit()
        

###############
## buttons

    def on_bt_working_dir_clicked(self, *args):
        dialog = self.obj('dlg_working_dir')
        response = dialog.run()
        path = dialog.get_filename()
        dialog.hide()
        if response != Gtk.ResponseType.OK:
            return
        self.obj('e_working_dir').set_text(path)

    def on_bt_command_clicked(self, *args):
        dialog = self.obj('dlg_command')
        response = dialog.run()
        path = dialog.get_filename()
        dialog.hide()
        if response != Gtk.ResponseType.OK:
            return
        self.obj('e_command').set_text(path) 


    def on_bt_filename_clicked(self, *args):
        dialog = self.obj('dlg_filename')
        response = dialog.run()
        path = dialog.get_filename()
        dialog.hide()
        if response != Gtk.ResponseType.OK:
            return
        self.obj('e_filename').set_text(path) 

    def on_bt_filename_dlg_user_app_clicked(self, *args):
        dialog = self.obj('dlg_filename')
        dir = settings.USER_APPLICATIONS_DIR
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except Exception, e:
                print e
                return
        dialog.set_current_folder(settings.USER_APPLICATIONS_DIR)
        
    def on_bt_filename_dlg_desktop_clicked(self, *args):
        dialog = self.obj('dlg_filename')
        dialog.set_current_folder(settings.USER_DESKTOP_DIR)


###############
## actions

    def on_ac_icon_activate(self, action, *args):
        self.select_icon()

    def on_ac_save_activate(self, action, *args):
        self.conn.store()
        path=self.obj('e_filename').get_text()
        self.dfile.save(path)

    def on_ac_quit_activate(self, action, *args):
        self.quit()

if __name__ == '__main__':
    IS_STANDALONE = True
    if len(sys.argv) < 2:
        sys.argv.append(None)
    editor = Editor(sys.argv[1])
    try:
        Gtk.main()
    except KeyboardInterrupt:
        Gtk.main_quit()
        






