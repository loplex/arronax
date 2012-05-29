#!/usr/bin/env python
#-*- coding: utf-8-*-

from gi.repository import Gtk, GdkPixbuf, GLib
import os, os.path, time, sys
from gettext import gettext as _
import gettext

import settings, connection, desktopfile, widgets, clipboard, about, dialogs
import converter, statusbar

IS_STANDALONE = False

MODE_EDIT = 'edit'
MODE_NEW = 'new'
MODE_CREATE_FOR = 'create for'
MODE_CREATE_IN = 'create_in'
MODE_OPEN = 'open'


class Editor(object):

    def __init__(self, path, mode):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
        gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
        gettext.textdomain(settings.GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'edit.ui'))
        self.builder.connect_signals(self)
        
        self.win = self.obj('window1')

        self.clip = clipboard.ContainerClipboard(self.obj('box_main'))
        self.clip.add_actions(cut=self.obj('ac_cut'),
                              copy=self.obj('ac_copy'),
                              paste=self.obj('ac_paste'),
                              delete=self.obj('ac_delete'))

        self.dfile = desktopfile.DesktopFile(self.win)
        self.factory = widgets.WidgetFactory(self.builder)

        statusbar.init(self.obj('statusbar'))

        self.conn = connection.ConnectionGroup(self.dfile)
        self.conn.add('Name', self.factory.get('e_title'))
        self.conn.add('Comment', self.factory.get('e_comment'))
        self.conn.add('Exec', self.factory.get('e_command'))
        self.conn.add('Hidden', self.factory.get('sw_advanced_hidden'),
                      type=bool)
        self.conn.add('Terminal', self.factory.get('sw_run_in_terminal'),
                      type=bool)
        self.conn.add('Icon', self.factory.get(
                'img_icon',
                defaulter=widgets.StringDefaulter(settings.DEFAULT_ICON)),
                      )
        self.conn.add('Path', self.factory.get('e_working_dir'))
        self.conn.add('Categories', self.factory.get('e_advanced_categories'))
        self.conn.add('StartupWMClass', self.factory.get('e_advanced_wm_class'))

        self.conn.add('MimeType', 
                      self.factory.get('tview_advanced_mime_types'),
                      converter=converter.ListConverter()
                      )
        self.conn.clear(store=True)

        if mode is MODE_EDIT:
            self.read_desktop_file(path)
        elif mode is MODE_CREATE_FOR:
            self.filename = None
            self.obj('e_command').set_text(path)
            self.create_title_from_command(path)
        elif mode is MODE_OPEN:
            self.filename = None
            self.create_title_from_command(path)
            self.obj('e_command').set_text("xdg-open '%s'" % path)
        else:
            self.filename = path
      
        self.win.show()


    def read_desktop_file(self, path):
        with statusbar.Status(_("Loading file '%s' ...") % path,
                              _("Loaded file '%s' ...") % path) as status:
            self.conn.clear(store=True)
            if not self.dfile.load(path):
                dialogs.error(
                    self.win, _('Can not load starter'),
                    _("Arronax doesn't support this kind of starter yet")
                    )
                status.set_end_msg(_("File not loaded."))
                self.conn.clear(store=True)
                return
                
            self.filename = path
            self.update_window_title()
            self.conn.view()


        
    def update_window_title(self): 
        if self.filename is None:
            title = settings.APP_NAME
        else:
            title = '%s: %s' % (settings.APP_NAME, self.filename)
        self.win.set_title(title)
        
        
        
    def create_title_from_command(self, command):
        if (command is None or 
            command == ''  or 
            self.obj('e_title').get_text() != ''):
            return
        title = os.path.basename(command)
        if title.endswith('.desktop'):
            title=title[:-len('.desktop')]
        self.obj('e_title').set_text(title.title())
        self.obj('e_title').select_region(0, len(title)+1)


    def obj(self, name):
        return self.builder.get_object(name)

    def check_data(self):
        msg=''
        try:
            if self.dfile['Name'] == '':
                msg = '%s\n%s' % (msg, _("You need to provide a name."))
        except desktopfile.KeyNotSetException:
            msg = '%s\n%s' % (msg, _("You need to provide a name."))
        
        try:    
            if self.dfile['Exec'] == '':
                msg = '%s\n%s' % (msg, _("You need to provide a command."))
        except desktopfile.KeyNotSetException:
            msg = '%s\n%s' % (msg, _("You need to provide a command."))
        return msg

        

    def check_dirty(self):
        if self.conn.is_dirty():
            answer = dialogs.yes_no_cancel_question(self.win,
                                                    _('Save now?'),
                                                    _('You have unsaved changes.  Do you want to save them now?')
                                                    )
            if answer == Gtk.ResponseType.YES:
                self.save()
            elif answer == Gtk.ResponseType.CANCEL:
                return
            
    def quit(self):
        self.check_dirty()
        
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
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    path,
                    settings.DEFAULT_ICON_SIZE,
                    settings.DEFAULT_ICON_SIZE)
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
        self.factory.get('img_icon').set_data(path)

    def about(self):
        about.show_about_dialog()

    def save(self):
        self.conn.store()
        msg = self.check_data()
        if msg != '':
            dialogs.error(self.win, _('Error'), msg)
            return
        
        if self.filename is None or os.path.isdir(self.filename):
            default = '%s.desktop' % self.obj('e_title').get_text()

            if self.filename is not None:  # folder
                default = os.path.join(self.filename, default)

            filename = self.ask_for_filename('dlg_save', True, default)
            if filename is None:
                return
            else:
                self.filename = filename
                self.update_window_title()
        
        with statusbar.Status(_("Saved file '%s'.")% self.filename):
            self.dfile.save(self.filename)



                           
    def ask_for_filename(self, dlg, add_ext=False, default=None):
        dialog = self.obj(dlg)
        if default is not None:
            folder = os.path.dirname(default)
            if folder == '':
                folder = settings.USER_DESKTOP_DIR
            dialog.set_current_folder(folder)

            file = os.path.basename(default)
            dialog.set_current_name(file)

        response = dialog.run()
        path = dialog.get_filename()
        dialog.hide()
        if response != Gtk.ResponseType.OK:
            return
        if add_ext and not path.endswith('.desktop'):
            path='%s.desktop' % path
        return path

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
        path = self.ask_for_filename('dlg_working_dir', False)
        if path is not None:
            self.obj('e_working_dir').set_text(path)

    def on_bt_command_clicked(self, *args):
        path = self.ask_for_filename('dlg_command', False)
        if path is not None:
            self.obj('e_command').set_text(path) 


    def on_bt_filename_dlg_user_app_clicked(self, *args):
        dialog = self.obj('dlg_save')
        dir = settings.USER_APPLICATIONS_DIR
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except Exception, e:
                print e
                return
        dialog.set_current_folder(settings.USER_APPLICATIONS_DIR)

    def on_bt_filename_dlg_desktop_clicked(self, *args):
        dialog = self.obj('dlg_save')
        dialog.set_current_folder(settings.USER_DESKTOP_DIR)
        
    def on_bt_dlg_open_desktop_clicked(self, *args):
        dialog = self.obj('dlg_open')
        dialog.set_current_folder(settings.USER_DESKTOP_DIR)

    def on_bt_dlg_open_user_app_clicked(self, *args):
        dialog = self.obj('dlg_open')
        dir = settings.USER_APPLICATIONS_DIR
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except Exception, e:
                print e
                return
        dialog.set_current_folder(settings.USER_APPLICATIONS_DIR)
        

     


###############
## actions

    def on_ac_icon_activate(self, action, *args):
        self.select_icon()

    def on_ac_save_activate(self, action, *args):
        self.save()

    def on_ac_quit_activate(self, action, *args):    
        self.quit()

    def on_ac_about_activate(self, action, *args):
        self.about()

    def on_ac_save_as_activate(self, action, *args):
        filename = self.ask_for_filename('dlg_save', True)
        if filename is not None:
            self.filename = filename
            self.update_window_title()
            self.save()            

    def on_ac_open_activate(self, action, *args):
        self.check_dirty()
        filename = self.ask_for_filename('dlg_open', True)
        if filename is not None:
            self.read_desktop_file(filename)

    def on_ac_new_activate(self, action, *args):
        self.check_dirty()
        self.filename = None
        self.conn.clear(True)
        self.update_window_title()
        


def main():
    global IS_STANDALONE
    IS_STANDALONE = True
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path):
            if os.path.splitext(path)[1] == '.desktop':                
                editor = Editor(path=path, mode=MODE_EDIT)
            else:
                editor = Editor(path=path, mode=MODE_OPEN)
        elif os.path.isdir(path):
            editor = Editor(path=path, mode=MODE_CREATE_IN)
        else:
            editor = Editor(path=path, mode=MODE_NEW) 
    else:
        editor = Editor(path=None, mode=MODE_NEW) 



    try:
        Gtk.main()
    except KeyboardInterrupt:
        Gtk.main_quit()    

if __name__ == '__main__':
    main()
        






