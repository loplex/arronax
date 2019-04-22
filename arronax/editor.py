#-*- coding: utf-8-*-
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
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, os.path, time, sys, urllib.request, urllib.parse, urllib.error, urllib.parse, argparse
from gettext import gettext as _
import gettext
import logging

from arronax import settings, desktopfile, clipboard, about, dialogs, iconbrowser
from arronax import statusbar, filechooser, tvtools, quicklist, utils, mimetypes
from arronax import categoriesbrowser, entrytools, parsecli

class Editor(object):

    def __init__(self, path, stype, basedir=None):

        logging.info('Editor: p:{} il:{} bd:{}'.format(
            path, stype, basedir))
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

        self.quicklist = quicklist.Quicklist(
            self['window1'], self['tv_quicklist'])
        self.dfile = desktopfile.DesktopFile()
        self.clip = clipboard.ContainerClipboard(self['box_main'], 
                                                 self.builder)
        statusbar.init(self['statusbar'])        
        about.add_help_menu(self['menu_help'])

        self.icon_has_changed = False
        
        self.setup_tv_show_in()
        self['cbox_type'].set_active(0)


        is_link = stype is parsecli.StarterType.Link
        is_app = stype is parsecli.StarterType.Application

        logging.debug('is_l:{} is_a:{}'.format(is_link, is_app))
        
        self['window1'].show()

        if utils.is_desktop_file(path):
            logging.debug('is desktop')
            self.read_desktop_file(path)
        else:
            if basedir:
                self.filename = basedir
            else:
                self.filename = None
                
            if path:
                self['e_command'].set_text(path)
                self.create_title_from_command(path)
            
            if not is_app and (is_link or not path or
                not os.path.isfile(path) or 
                not os.access(path, os.X_OK)):
                logging.debug('Link')
                self['cbox_type'].set_active(1)
                self.dfile.type = 1
                icon = 'folder'
            else:
                logging.debug('App')
                self['cbox_type'].set_active(0)
                self.dfile.type = 0
                icon = 'application-x-executable'

            self.set_icon(icon)
            self.dfile.icon = icon
        self.dfile.dirty_flag = False


    def create_builder(self):
        self.builder = Gtk.Builder()
        logging.debug('LOCALES: domain:{} dir:{}'.format(
            settings.GETTEXT_DOMAIN,
            settings.LOCALE_DIR))
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
        gettext.bindtextdomain(settings.GETTEXT_DOMAIN,
                               settings.LOCALE_DIR)
        gettext.textdomain(settings.GETTEXT_DOMAIN)
        gettext.bind_textdomain_codeset(settings.GETTEXT_DOMAIN, 'UTF-8')

        self.builder.add_from_file(os.path.join(settings.UI_DIR, 
                                                'edit.ui'))
        self.builder.connect_signals(self)
        entrytools.add_clear_button_to_builder_obj(self.builder)


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
        for field, name in sorted(settings.KNOWN_DESKTOPS.items()):
            model.append([True, name, field])
    
    def update_from_dfile(self):
        data = self.dfile.get_as_dict()
        self.set_data_for_all_widgets(data)
        self.update_window_title()
        self.icon_has_changed = False


    def read_desktop_file(self, path):
        logging.info("Loading {}".format(path))
        start_msg = _("Loading file '{path}' ...").format(path=path)
        end_msg = _("Loaded file '{path}' ...").format(path=path)
        with statusbar.Status(start_msg, end_msg) as status:
            msg = self.dfile.load(path)
            if msg is not None:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                err_msg = _("Can't load file '{path}':\n {error}").format(
                    path=path, error=msg)
                dialogs.error(self['window1'], _('Error'), err_msg)
                end_msg = _("Can't load file '{path}'").format(path=path)
                status.set_end_msg(end_msg)

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
                logging.error(
                    'use_file_or_uri_as_target: error:{}'.format(e))
            if is_exec:
                self['cbox_type'].set_active(0)
            else:
                self['cbox_type'].set_active(1)

        
    def update_window_title(self): 
        if self.filename is None:
            title = settings.APP_NAME
        else:
            title = '{app_name}: {file_name}'.format(
                app_name=settings.APP_NAME, file_name=self.filename)
        logging.debug('New title: "{}"'.format(title))
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
        # if not self.icon_has_changed:
        #     data['icon'] = ''
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
            logging.error("Exception on qut: {}".format(e))
            really_quit = True
        if really_quit:        
            Gtk.main_quit()            

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
            
    def icon_browse_apps(self):
        current = utils.get_name_from_image(self['img_icon'])
        app = utils.select_app(self['window1'], current)
        if not app:
            return

        uri = urllib.parse.urlparse('application://'+app)
        path = utils.get_path_for_application_uri(uri)
        icon = utils.get_field_from_desktop_file(path, 'Icon')
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
            except GLib.GError as e:
                print(e)
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
        logging.debug('set_icon: {}'.format(path))
        if path is None:
            return
        self['l_icon'].set_text(path)
        self['l_icon'].set_tooltip_text(path)
        img = self['img_icon']
        msg = utils.load_file_into_image(img, path)
        self.icon_has_changed = True
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
        logging.debug('all data: {}'.format(data))
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

        status_msg = _("Saving file '{path}' ...").format(
            path=self.filename or '')
        end_msg = _("File '{path}' saved.").format(
            path=self.filename or '')

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
                    end_msg = _("Saved file '{path}'.").format(
                        path=self.filename)
                    status.set_end_msg(end_msg)
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
            uri = urllib.parse.urlparse(uris[0])
            filename = None
            if uri.scheme == 'file':
                filename = urllib.request.url2pathname(uri.path)
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
            uri = urllib.parse.urlparse(uris[0])
            if uri.scheme == 'file':
                text = urllib.request.url2pathname(uri.path)
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

    def on_bt_icon_browse_files_clicked(self, *args):
         self.icon_browse_files()
         
    def on_bt_icon_browse_icons_clicked(self, *args):
         self.icon_browse_icons()

    def on_bt_icon_browse_auto_clicked(self, *args):
         self.icon_browse_auto()

    def on_bt_icon_by_app_clicked(self, *args):
         self.icon_browse_apps()
         
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
        cats = [c.strip() for c in cats.split(';') if c.strip() != '']
        dlg = categoriesbrowser.CategoriesDlg(self['window1'], cats)
        cats = dlg.run()
        if cats is not None:
            self['e_categories'].set_text('; '.join(cats))

        
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
            uri = urllib.parse.urlparse(uris[0])
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
            
    def on_ac_open_app_activate(self, action, *args):
        if self.maybe_confirm_unsaved():
            app = utils.select_app(self['window1'], None)
            if app is not None:
                uri = urllib.parse.urlparse('application://'+app)
                path = utils.get_path_for_application_uri(uri)
                self.read_desktop_file(path)
            
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
    args = parsecli.parse_cli_args()
    editor = Editor(args.path, args.stype, args.dir)
    

    try:
        Gtk.main()
    except KeyboardInterrupt:
        Gtk.main_quit()    


