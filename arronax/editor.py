#-*- coding: utf-8-*-

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib, urlparse
from gettext import gettext as _
import gettext

import settings, desktopfile, clipboard, about, dialogs, iconbrowser
import statusbar, filechooser, tvtools, quicklist, utils, mimetypes
import categoriesbrowser

IS_STANDALONE = False

MODE_EDIT = 'edit'
MODE_NEW = 'new'
MODE_CREATE_FOR = 'create for'
MODE_CREATE_IN = 'create_in'

TYPE_APPLICATION = 0
TYPE_LINK = 1

class Editor(object):

    def __init__(self, path, mode, type=TYPE_APPLICATION):
        self.create_builder()

        utils.activate_drag_and_drop(self['window1'])
        utils.activate_drag_and_drop(self['bt_icon'])
        utils.activate_drag_and_drop(
            self['e_title'], self.on_entry_drag_data_received, 'Name')
        utils.activate_drag_and_drop(
            self['e_command'], self.on_entry_drag_data_received, 
            'Exec')
        utils.activate_drag_and_drop(
            self['e_working_dir'], self.on_entry_drag_data_received,
            'Path')
        utils.activate_drag_and_drop(
            self['e_categories'], self.on_entry_drag_data_received, 
            'Categories')
        utils.activate_drag_and_drop(
            self['e_wm_class'], self.on_entry_drag_data_received, 
            'StartupWMClass')
        utils.activate_drag_and_drop(
            self['e_comment'], self.on_entry_drag_data_received, 
            'Comment')
        utils.activate_drag_and_drop(self['tview_mime_types'])

        self.quicklist = quicklist.Quicklist(self['tv_quicklist'])
        self.dfile = desktopfile.DesktopFile()
        self.clip = clipboard.ContainerClipboard(self['box_main'], 
                                                 self.builder)
        statusbar.init(self['statusbar'])        
        about.add_help_menu(self['menu_help'])
        self.setup_tv_show_in()
        self['cbox_type'].set_active(0)
        if mode is MODE_EDIT:
            self.read_desktop_file(path)
        elif mode is MODE_CREATE_FOR:
            self.filename = None
            self['e_command'].set_text(path)
            self.create_title_from_command(path)
            if type == TYPE_LINK:
                self['cbox_type'].set_active(1)
            utils.load_file_into_image(
                self['img_icon'], 'application-x-executable')
        else:
            self.filename = path
            utils.load_file_into_image(
                self['img_icon'], 'folder')
        self['window1'].show()


    def create_builder(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
        gettext.bindtextdomain(settings.GETTEXT_DOMAIN)
        gettext.textdomain(settings.GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'edit.ui'))
        self.builder.connect_signals(self)


    def setup_tv_show_in(self):
        tv = self['tv_show_in']
        model = Gtk.ListStore(bool, str, str)
        tv.set_model(model)
        tvtools.create_treeview_column(tv, _('Enabled'), 0,
                                       utils.create_toggle_renderer(tv),
                                       activatable=True,
                                       attr='active'
                                   )
        tvtools.create_treeview_column(tv, _('Name'), 1)
        for field, name in sorted(settings.KNOWN_DESKTOPS.iteritems()):
            model.append([True, name, field])
    
    def update_from_dfile(self):
        data = self.dfile.get_as_dict()
        self.set_data_for_all_widgets(data)
        self.update_window_title()        


    def read_desktop_file(self, path):
        with statusbar.Status(_("Loading file '%s' ...") % path,
                              _("Loaded file '%s' ...") % path) as status:
            msg = self.dfile.load(path)
            if msg is not None:
                return False
            else:
                self.filename = path
                self.update_from_dfile()
                return True


    def use_file_or_uri_as_target(self, s, is_uri=False):
        self.filename = None
        self['e_command'].set_text(s)
        if is_uri:
            self.create_title_from_command(s, True)
            self['cbox_type'].set_active(1)
        else:
            self.create_title_from_command(s, False)
            is_exec = False
            try:
               is_exec = not os.path.isdir(s) and os.access(s, os.X_OK)
            except Exception as e:
                print(e)
            if is_exec:
                self['cbox_type'].set_active(0)
            else:
                self['cbox_type'].set_active(1)



        
    def update_window_title(self): 
        if self.filename is None:
            title = settings.APP_NAME
        else:
            title = '%s: %s' % (settings.APP_NAME, self.filename)
        self['window1'].set_title(title)
        
               
    def create_title_from_command(self, command, is_uri=False):
        if command in (None, ''):
            return
        if is_uri:
            title = command
        else:
            title = os.path.basename(command)
        self['e_title'].set_text(title)
        self['e_title'].select_region(0, len(title)+1)


    def check_data(self):
        msg=[]
        if self['e_title'].get_text() == '':
            msg.append(_("You need to provide a title."))
        if self['e_command'].get_text() == '':
            if self.dfile.type == 0:
                msg.append(_("You need to provide a command."))
            else:
                msg.append(_("You need to provide a URL or file name."))
        return '\n'.join(msg)

    def maybe_confirm_unsaved(self):
        data = self.get_data_from_all_widgets()
        answer = None
        if self.dfile.is_dirty(data):
            answer = dialogs.yes_no_cancel_question(
                self['window1'], _('Save now?'),
                _('You have unsaved changes.  Do you want to save them now?')
                )
            if answer == Gtk.ResponseType.YES:
                return self.save()
        return answer != Gtk.ResponseType.CANCEL
            
    def quit(self):
        try: # just to be sure
            really_quit =  self.maybe_confirm_unsaved()
        except Exception as e:
            really_quit = True
        if really_quit:        
            if IS_STANDALONE:
                Gtk.main_quit()            
            else:
                self['window1'].destroy()

    def icon_browse_auto(self):
        current = utils.get_name_from_image(self['img_icon'])
        if '/' in current:
            self.icon_browse_files()
        else:
            self.icon_browse_icons()

            
    def icon_browse_icons(self):
        current = utils.get_name_from_image(self['img_icon'])
        icon = iconbrowser.IconDlg(self['window1']).run(current)
        if icon is not None:
            self.set_icon(icon)
    
    def icon_browse_files(self):
        current = utils.get_name_from_image(self['img_icon'])
        if not '/' in current:
            for dir in Gtk.IconTheme.get_default().get_search_path():
                if os.path.exists(dir):
                    current = dir
                    break
        
        preview = Gtk.Image()

        dialog = Gtk.FileChooserDialog(_("Select Icon"), self['window1'],
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, 
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, 
                                        Gtk.ResponseType.OK))
        dialog.set_preview_widget(preview)
        dialog.set_use_preview_label(False)
        dialog.set_filename(current)

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

    def __getitem__(self, key):
        return self.builder.get_object(key)

    def set_icon(self, path):
        img = self['img_icon']
        msg = utils.load_file_into_image(img, path)
        if msg is not None:
            statusbar.show_msg(msg)

    def about(self):
        about.show_about_dialog()

    def get_data_from_all_widgets(self):
        data = {
            'type': self['cbox_type'].get_active(),
            'title': self['e_title'].get_text(),
            'command': self['e_command'].get_text(),
            'working_dir':  self['e_working_dir'].get_text(),
            'run_in_terminal': self['sw_run_in_terminal'].get_active(),
            'hidden': self['sw_hidden'].get_active(),
            'icon': utils.get_name_from_image(self['img_icon']),
            'keywords': utils.make_keyfile_list_string(
                utils.get_list_from_textview(self['tview_keywords'])),
            'categories': self['e_categories'].get_text(),
            'wm_class': self['e_wm_class'].get_text(),
            'comment': self['e_comment'].get_text(),
            'mime_type':utils.make_keyfile_list_string(
                utils.get_list_from_textview(self['tview_mime_types'])),
            'show_in': utils.get_desktops_from_tv(self['tv_show_in']),
            'quicklist': utils.get_quicklist_from_tv(self['tv_quicklist'])
        }
        return data


    def set_data_for_all_widgets(self, data):
        self['cbox_type'].set_active(data['type'])
        self['e_title'].set_text(data['title'])
        self['e_command'].set_text(data['command'])
        self['e_working_dir'].set_text(data['working_dir'])
        self['sw_run_in_terminal'].set_active(data['run_in_terminal'])
        self['sw_hidden'].set_active(data['hidden'])
        self.set_icon(data['icon'])
        utils.set_list_to_textview(self['tview_keywords'], data['keywords'])
        self['e_categories'].set_text(data['categories'])
        self['e_wm_class'].set_text(data['wm_class'])
        self['e_comment'].set_text(data['comment'])
        utils.set_list_to_textview(self['tview_mime_types'], 
                                   data['mime_type'])
        utils.load_desktops_into_tv(self['tv_show_in'], data['show_in'])
        utils.load_quicklist_into_tv(self['tv_quicklist'], data['quicklist'])
   
    def get_default_filename(self):
        fname_from_title = '%s.desktop' % self['e_title'].get_text()
        if self.filename is None:
            return fname_from_title
        elif os.path.isdir(self.filename):
            return os.path.join(self.filename, fname_from_title)
        else:
            return self.filename

    def show_msg(self, msg):
        if msg is not None:
            msg = str(msg)
            statusbar.show_msg(msg)

    def save(self, is_save_as=False): 
        data = self.get_data_from_all_widgets()
        self.dfile.set_from_dict(data)

        msg = self.check_data()
        if msg != '':
            dialogs.error(self['window1'], _('Error'), msg)
            return False

        status_msg = _("Saving file %s ...") % (self.filename or '')
        end_msg = _("File %s saved.") % (self.filename or '')

        with statusbar.Status(status_msg, end_msg) as status:            
            if (is_save_as or (self.filename is None or 
                               os.path.isdir(self.filename))):
                default = self.get_default_filename()

                filename = filechooser.ask_for_filename(
                    'dlg_save', default=default)
                if filename is None:
                    status.set_end_msg(_("File not saved."))
                    return
                else:
                    self.filename = filename
                    status.set_end_msg(_("Saved file '%s'.")% self.filename)
                    self.update_window_title()
            msg = self.dfile.save(self.filename)
            if msg is not None:
                dialogs.error(self['window1'], _('Can not save starter'), 
                              msg)
                status.set_end_msg(_("File not saved."))
                return False
        self.read_desktop_file(self.filename)
        return True
            
#####################
## signal handlers
#####################

###############
## main window

    def on_window1_delete_event(self, *args):
        self.quit()

    def on_window1_drag_data_received(self, widget, drag_context, x, y, data,
                                      info, time): 

        if info != 0:
            return
        
        uris = data.get_uris()
        if len(uris) > 0:           
            uri = urlparse.urlparse(uris[0])
            filename = None
            if uri.scheme == 'file':
                filename = urllib.url2pathname(uri.path)
            elif uri.scheme == 'application':
                filename = utils.get_path_for_application_uri(uri)
            else:  # some other URI
                if self.maybe_confirm_unsaved():
                    self.use_file_or_uri_as_target(uri.geturl(), True)
            if filename:
                if self.maybe_confirm_unsaved():
                    if not self.read_desktop_file(filename):
                       # not a valid .desktop file
                       self.use_file_or_uri_as_target(filename)
        else: # no uris
            text = data.get_text()
            if (text is not None and
                    text != '' and
                    self.maybe_confirm_unsaved()):
                self.use_file_or_uri_as_target(text, True)

                
    def on_urientry_drag_data_received(self, widget, drag_context, x, y, 
                                       data, info, time):
        uris = data.get_uris()
        if uris:
            uri = urlparse.urlparse(uris[0])
            if uri.scheme == 'file':
                text = urllib.url2pathname(uri.path)
            else:
                text = uris[0]
            widget.set_text(text)


    def on_entry_drag_data_received(self, widget, drag_context, x, y, 
                                       data, info, time, field):
        uris = data.get_uris()
        if info == 0 and len(uris) > 0: 
            title = utils.get_info_from_uri(uris[0], field)
            widget.set_text(title) 
        
    def on_tview_mime_types_drag_data_received(self, widget, 
                                               drag_context, x, y, data,
                                               info, time):
        uris = data.get_uris()
        mime_types = utils.get_mime_types_from_uris(uris, self.show_msg)
        data = ';'.join(utils.get_list_from_textview(
            self['tview_mime_types']))
        current = data.split(';')
        mime_types.update(i for i in current if i.strip() != '')
        utils.set_list_to_textview(self['tview_mime_types'], 
                                   sorted(mime_types))


###############
## type list

    def on_cbox_type_changed(self, widget):
        app_only = ('e_working_dir', 'l_working_dir', 'bt_working_dir',
                    'sw_run_in_terminal', 'l_run_in_terminal',
                    'e_wm_class', 'l_wm_class',
                    'l_tab_quicklist', 'box_quicklist',
                    'l_tab_mime_types', 'box_mime_types',
                )
        is_app = widget.get_active() == 0
        command_label = ( _('File or URL:'), _('Command:'),)[is_app]
        for name in app_only:
            self[name].set_sensitive(is_app)
        self['l_command'].set_label(command_label)
            
###############
## buttons

    def on_bt_working_dir_clicked(self, *args):
        default =  self['e_working_dir'].get_text()
        if default =='':  
            cmd = self['e_command'].get_text()
            cmd_dir=os.path.dirname(cmd)
            if os.path.isdir(cmd_dir):
                default = '%s/' % cmd_dir
            else:
                default = None

        path = filechooser.ask_for_filename(
            'dlg_working_dir', False, default)
        if path is not None:
            self['e_working_dir'].set_text(path)

    def on_bt_command_clicked(self, *args):
        cmd = self['e_command'].get_text()
        path = filechooser.ask_for_filename(
            'dlg_command', False, default=cmd)
        if path is not None:
            self['e_command'].set_text(path) 

    def on_bt_mime_types_select_clicked(self, *args):
        mime_types = utils.get_list_from_textview(self['tview_mime_types'])
        dlg = mimetypes.MimetypesDlg(mime_types)
        mime_types = dlg.run()
        if mime_types is not None:
            utils.set_list_to_textview(self['tview_mime_types'], 
                                       sorted(mime_types))

    def on_bt_categories_clicked(self, *args):
        cats = self['e_categories'].get_text()
        cats = [c.strip() for c in cats.split(',') if c.strip() != '']
        dlg = categoriesbrowser.CategoriesDlg(self['window1'], cats)
        cats = dlg.run()
        if cats is not None:
            self['e_categories'].set_text(', '.join(cats))

        
    def on_bt_uri_clicked(self, *args):
        uri = self['e_command'].get_text()
        if uri == '':
            uri = None            
        path = filechooser.ask_for_filename(
            'dlg_file', False, default=uri)
        if path is not None:
            self['e_command'].set_text(path) 
     
    def on_bt_icon_drag_data_received(self, widget, drag_context, x, y, data,
                                      info, time):
        uris = data.get_uris()
        if info == 0 and len(uris) > 0:
            uri = urlparse.urlparse(uris[0])
            if uri.scheme == 'application':
                path = utils.get_path_for_application_uri(uri)
                icon = utils.get_field_from_desktop_file(path, 'Icon')
                self.set_icon(icon)
            elif uri.scheme == 'file':
                path = uri.path
                if utils.is_desktop_file(uri.geturl()):
                    path = utils.get_field_from_desktop_file(path, 'Icon')
                    self.set_icon(path)
                else:
                    mime = utils.get_mime_type(uri)
                    if mime.startswith('image/'):
                        self.set_icon(path)
                    else:
                        statusbar.show_msg(
                            _('This is not an image. Icon not changed.'))
            else:
                statusbar.show_msg(
                    _('This is not a local file. Icon not changed.'))
                return

###############
## actions

    def on_ac_icon_activate(self, action, *args):
        self.icon_browse_auto()


    def on_ac_icon_browse_activate(self, action, *args):
        mode = self['cbox_icon_browse_mode'].get_active_id()
        print('MODE:', mode)
        if mode == 'files':
            self.icon_browse_files()
        elif mode == 'icons':
            self.icon_browse_icons()
        else:
            self.icon_browse_auto()

    def on_ac_save_activate(self, action, *args):
        self.save()

    def on_ac_quit_activate(self, action, *args):    
        self.quit()

    def on_ac_about_activate(self, action, *args):
        self.about()

    def on_ac_save_as_activate(self, action, *args):
        self.save(True)

    def on_ac_open_activate(self, action, *args):
        if self.maybe_confirm_unsaved():
            filename = filechooser.ask_for_filename(
                'dlg_open', True, default=None)
                                         
        if filename is not None:
            self.read_desktop_file(filename)

    def on_ac_new_activate(self, action, *args):
        if self.maybe_confirm_unsaved():
            self.filename = None
            self.dfile.clear()
            self.update_from_dfile()
            statusbar.show_msg(_('Created new starter.'))
            self.update_window_title()
        

    def on_ac_quicklist_up_activate(self, action, *args):
        self.quicklist.goto_prev_row()
                
    def on_ac_quicklist_down_activate(self, action, *args):
        self.quicklist.goto_next_row()

    def on_ac_quicklist_remove_activate(self, action, *args):
        self.quicklist.remove_current_row()

    def on_ac_quicklist_new_activate(self, action, *args):
        self.quicklist.new_row()

    def on_ac_quicklist_edit_activate(self, action, *args):
        self.quicklist.edit_current_row()
        
    def on_ac_quicklist_duplicate_activate(self, action, *args):
        self.quicklist.duplicate_current_row()


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


