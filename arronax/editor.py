#!/usr/bin/env python
#-*- coding: utf-8-*-

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib, urlparse
from gettext import gettext as _
import gettext

import settings, connection, desktopfile, widgets, clipboard, about, dialogs
import converter, statusbar, filechooser

IS_STANDALONE = False

MODE_EDIT = 'edit'
MODE_NEW = 'new'
MODE_CREATE_FOR = 'create for'
MODE_CREATE_IN = 'create_in'

TYPE_APPLICATION = 0
TYPE_LINK = 1

class Editor(object):

    def __init__(self, path, mode, type=TYPE_APPLICATION):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
        gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
        gettext.textdomain(settings.GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'edit.ui'))
        self.builder.connect_signals(self)
        
        self.win = self.obj('window1')
        self.win.drag_dest_set(Gtk.DestDefaults.ALL, [],  
                               Gdk.DragAction.COPY)
        self.win.drag_dest_add_uri_targets()


        bt_icon = self.obj('bt_icon')
        bt_icon.drag_dest_set(Gtk.DestDefaults.ALL, [],  
                               Gdk.DragAction.COPY)
        bt_icon.drag_dest_add_uri_targets()

        self.tview_mime = self.obj('tview_advanced_mime_types')
        self.tview_mime.drag_dest_set(Gtk.DestDefaults.ALL, [],  
                                      Gdk.DragAction.COPY)
        self.tview_mime.drag_dest_add_uri_targets()

        self.clip = clipboard.ContainerClipboard(self.obj('box_main'))
        self.clip.add_actions(cut=self.obj('ac_cut'),
                              copy=self.obj('ac_copy'),
                              paste=self.obj('ac_paste'),
                              delete=self.obj('ac_delete'))

        self.dfile = desktopfile.DesktopFile(self.win)
        self.factory = widgets.WidgetFactory(self.builder)

        statusbar.init(self.obj('statusbar'))

        self.conn = connection.ConnectionGroup(self.dfile)

        self.conn.add('Type', self.factory.get('cbox_type'),
                      converter=converter.DictConverter({0: 'Application',
                                                         1: 'Link'})
                      )
 
        self.conn.add('Name', self.factory.get('e_title'))
        self.conn.add('Comment', self.factory.get('e_comment'))
        self.conn.add('Exec', self.factory.get('e_command'), 
                      tags=['application'], 
                      related=(self.factory.get('l_command'),
                               self.factory.get('bt_command')
                               )
                      )
        self.conn.add('URL', self.factory.get('e_uri'), 
                      tags=['link'], 
                      related=(self.factory.get('l_uri'),
                               self.factory.get('bt_uri')
                               )
                      )
        self.conn.add('Hidden', self.factory.get('sw_advanced_hidden'),
                      type=bool, tags=['application'], 
                      related=self.factory.get('l_advanced_hidden'))
        self.conn.add('Terminal', self.factory.get('sw_run_in_terminal'),
                      type=bool, tags=['application'],
                      related=self.factory.get('l_run_in_terminal'))
        self.conn.add('Icon', self.factory.get(
                'img_icon',
                defaulter=widgets.StringDefaulter(settings.DEFAULT_ICON)),
                      )
        self.conn.add('Keywords', self.factory.get('tview_keywords'),
                      converter=converter.ListConverter()
                      )
        self.conn.add('Path', self.factory.get('e_working_dir'), 
                      tags=['application'],
                      related=(self.factory.get('l_working_dir'),
                               self.factory.get('bt_working_dir')
                               )
                      )
        self.conn.add('Categories', self.factory.get('e_advanced_categories'))
        self.conn.add('StartupWMClass', self.factory.get('e_advanced_wm_class'),
                      tags=['application'],
                      related=self.factory.get('l_advanced_wm_class'))

        self.conn.add('MimeType', 
                      self.factory.get('tview_advanced_mime_types'),
                      converter=converter.ListConverter(),
                      tags=['application']
                      )
        self.conn.add_no_data(self.factory.get('notebook', 
                                               klass=widgets.NotebookPageWidget,
                                               page_num=3),
                              tags=['application']
                              )
        self.conn.add('OnlyShowIn',
                      self.factory.get('tview_advanced_show_in',
                                       klass=widgets.SelectionListWidget,
                                       items={'GNOME': _('GNOME'),
                                              'KDE': _('KDE'), 
                                              'LXDE': _('LXDE'),
                                              'MATE': _('MATE'),
                                              'Razor': _('Razor-qt'),
                                              'ROX': _('ROX'),
                                              'TDE': _('Trinity Desktop'),
                                              'Unity': _('Unity'), 
                                              'XFCE': _('XFCE'),
                                              'Old': _('Legacy environments'),
                                              },
                                       ),
                      converter=converter.OneLineListConverter(),
                      )
                      
        self.conn.clear(store=True)

        self.type_watcher = widgets.get_watcher(
            self.factory.get('cbox_type'),
            connection_groups=[self.conn],
            tags={'application': lambda x: x == 0,
                  'link': lambda x: x == 1
                  }
            )

        ## make sure the type is changed so we get the signal
        self.factory.get('cbox_type').set_data(-1) 
        self.factory.get('cbox_type').set_data(type)

        if mode is MODE_EDIT:
            self.read_desktop_file(path)
        elif mode is MODE_CREATE_FOR:
            self.filename = None
            self.obj('e_command').set_text(path)
            self.create_title_from_command(path)
        else:
            self.filename = path
      
        self.win.show()


    def read_desktop_file(self, path):
        with statusbar.Status(_("Loading file '%s' ...") % path,
                              _("Loaded file '%s' ...") % path) as status:
            self.conn.clear(store=True)
            msg = self.dfile.load(path)
            if msg is not None:
                dialogs.error(self.win, _('Can not load starter'), msg)
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
                raise desktopfile.KeyNotSetException()
        except desktopfile.KeyNotSetException:
            msg = '%s\n%s' % (msg, _("You need to provide a title."))
        
        try:    
            if (self.dfile['Type'] == 'Application' and 
                self.dfile['Exec'] == ''):
                raise desktopfile.KeyNotSetException()  
        except desktopfile.KeyNotSetException:
            msg = '%s\n%s' % (msg, _("You need to provide a command."))

        try:    
            if (self.dfile['Type'] == 'Link' and 
                self.dfile['URL'] == ''):
                raise desktopfile.KeyNotSetException()  
        except desktopfile.KeyNotSetException:
            msg = '%s\n%s' % (msg, _("You need to provide a URL or file name."))

        
        return msg

        

    def check_dirty(self):
        if self.conn.is_dirty():
            answer = dialogs.yes_no_cancel_question(
                self.win,
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
        msg = self.factory.get('img_icon').set_data(path)
        if msg is not None:
            statusbar.show_msg(msg)
        else:
            settings.LAST_ICON = path

    def about(self):
        about.show_about_dialog()

        
    def save(self, is_save_as=False):        
        self.conn.store()
        msg = self.check_data()
        if msg != '':
            dialogs.error(self.win, _('Error'), msg)
            return
        
        if self.filename is None:
            status_msg = _("Saving file ...")
            end_msg = _("File saved.")
        else:
            status_msg = _("Saving file '%s'...")% self.filename
            end_msg = _("Saved file '%s'.")% self.filename
        with statusbar.Status(status_msg, end_msg) as status:
            
            if (is_save_as or (self.filename is None or 
                               os.path.isdir(self.filename))):
                fname_from_title = '%s.desktop' % self.obj('e_title').get_text()
                if self.filename is None:
                    default = fname_from_title
                elif os.path.isdir(self.filename):
                    default = os.path.join(self.filename, fname_from_title)
                else:
                    default = self.filename

                filename = self.ask_for_filename('dlg_save', True, default, 
                                                 Gtk.FileChooserAction.SAVE)
                if filename is None:
                    status.set_end_msg(_("File not saved."))
                    return
                else:
                    self.filename = filename
                    status.set_end_msg(_("Saved file '%s'.")% self.filename)
                    self.update_window_title()
        
            msg = self.dfile.save(self.filename)
            if msg is not None:
                dialogs.error(self.win, _('Can not save starter'), msg)
                status.set_end_msg(_("File not saved."))

                           
    def ask_for_filename(self, defname, add_ext=False, default=None):
        dlgdef = settings.FILE_DLG_DEF[defname]
        dialog = filechooser.create_dir_buttons_filechooser_dlg(
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

    def on_window1_drag_data_received(self, widget, drag_context, x, y, data,
                                      info, time):
        uris = data.get_uris()
        if info == 0 and len(uris) > 0:
            uris = data.get_uris()
            uri = urlparse.urlparse(uris[0])
            if uri.scheme == 'file':
                filename = urllib.url2pathname(uri.path)
                self.check_dirty()
                self.read_desktop_file(filename)


    def on_tview_advanced_mime_types_drag_data_received(self, widget, 
                                                       drag_context, x, y, data,
                                                       info, time):
        mime_types = set()
        uris = data.get_uris()
        for uri in uris:
            try:
                gfile = Gio.File.new_for_uri(uri)
                info = gfile.query_info("standard::*", 
                                        Gio.FileQueryInfoFlags.NONE, None)
                mime_types.add(info.get_content_type())
            except GLib.GError as e:
                print e
        tview = self.factory.get('tview_advanced_mime_types')
        data = tview.get_data()
        current = [x for x in data.splitlines() if x.strip() != '']
        mime_types.update(current)
        tview.set_data('\n'.join(sorted(mime_types)))

            
        

###############
## buttons


    def on_bt_working_dir_clicked(self, *args):
        default =  self.obj('e_working_dir').get_text()
        if default =='':  
            cmd = self.obj('e_command').get_text()
            cmd_dir=os.path.dirname(cmd)
            if os.path.isdir(cmd_dir):
                default = '%s/' % cmd_dir
            else:
                default = None

        path = self.ask_for_filename('dlg_working_dir', False, default)
        if path is not None:
            self.obj('e_working_dir').set_text(path)

    def on_bt_command_clicked(self, *args):
        cmd = self.obj('e_command').get_text()
        path = self.ask_for_filename('dlg_command', False, default=cmd)
        if path is not None:
            self.obj('e_command').set_text(path) 

    def on_bt_uri_clicked(self, *args):
        uri = self.obj('e_uri').get_text()
        if uri == '':
            uri = None            
        path = self.ask_for_filename('dlg_file', False, default=uri)
        print 'PATH:', path
        if path is not None:
            self.obj('e_uri').set_text(path) 


     
    def on_bt_icon_drag_data_received(self, widget, drag_context, x, y, data,
                                      info, time):
        uris = data.get_uris()
        if info == 0 and len(uris) > 0:
            uri = data.get_uris()[0]
            gfile = Gio.File.new_for_uri(uri)
            path = gfile.get_path()
            if path is None:
               statusbar.show_msg(_('This is not a local file. Icon not changed.'))
               return
            info = gfile.query_info("standard::*", 
                                    Gio.FileQueryInfoFlags.NONE, None)
            mime = info.get_content_type()
            if not mime.startswith('image/'):
                statusbar.show_msg(_('This is not an image. Icon not changed.'))
                return
            self.set_icon(path)



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
        self.save(True)

    def on_ac_open_activate(self, action, *args):
        self.check_dirty()
        filename = self.ask_for_filename('dlg_open', True, default=None,
                                         action=Gtk.FileChooserAction.OPEN)
        if filename is not None:
            self.read_desktop_file(filename)

    def on_ac_new_activate(self, action, *args):
        statusbar.show_msg(_('Created new starter.'))
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
                if os.access(path, os.X_OK):
                    type=TYPE_APPLICATION
                else:
                    type=TYPE_LINK
                editor = Editor(path=path, mode=MODE_CREATE_FOR, 
                                type=type) 
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
        






