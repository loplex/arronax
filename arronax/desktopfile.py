#!/usr/bin/env python

#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio, GLib
from gettext import gettext as _

import os, os.path, stat

import dialogs

GROUP = 'Desktop Entry'
AYATANA_GROUP_SUFFIX = ' Shortcut Group'

class DesktopFile(object):

    def __init__(self):
        self.keyfile = GLib.KeyFile()
        self.dirty_flag = False

    def remove_key(self, key, group=GROUP):
        try:
            self.keyfile.remove_key(group, key)
        except:
            pass

    @property
    def type(self):
        try:
            t = self.keyfile.get_string(GROUP, 'Type')
        except:
            t = 0
        return {'Application':0, 'Link':1}.get(t, 0)

    @type.setter
    def type(self, atype):
        name = ('Application', 'Link')[atype]
        self.keyfile.set_string(GROUP, 'Type', name)
        self.dirty_flag = True

    @property
    def title(self):
        try:
            return self.keyfile.get_string(GROUP, 'Name')
        except:
            return ''

    @title.setter
    def title(self, atitle):
        if atitle == '':
            self.remove_key('Name')
        else:
            self.keyfile.set_string(GROUP, 'Name', atitle)
        self.dirty_flag = True

    @property
    def command(self):
        key = ('Exec', 'URL')[self.type]
        try:
            return self.keyfile.get_string(GROUP, key)
        except:
            return ''

    @command.setter
    def command(self, acommand):
        key = ('Exec', 'URL')[self.type]
        self.remove_key('Exec')
        self.remove_key('URL')
        if acommand != '':
            self.keyfile.set_string(GROUP, key, acommand)
        self.dirty_flag = True

    @property
    def working_dir(self):
        try:
            return self.keyfile.get_string(GROUP, 'Path')
        except:
            return ''

    @working_dir.setter
    def working_dir(self, aworking_dir):
        if aworking_dir == '':
            self.remove_key('Path')
        else:
            self.keyfile.set_string(GROUP, 'Path', aworking_dir)
        self.dirty_flag = True

    @property
    def icon(self):
        try:
            return self.keyfile.get_string(GROUP, 'Icon')
        except:
            return ''

    @icon.setter
    def icon(self, aicon):
        if aicon == '':
            self.remove_key('Icon')
        else:
            self.keyfile.set_string(GROUP, 'Icon', aicon)
        self.dirty_flag = True

    @property
    def keywords(self):
        try:
            return self.keyfile.get_string(GROUP, 'Keywords')
        except:
            return ''

    @keywords.setter
    def keywords(self, akeywords):
        if akeywords in  ['', ';']:
            self.remove_key('Keywords')
        else:
            self.keyfile.set_string(GROUP, 'Keywords', akeywords)
        self.dirty_flag = True

    @property
    def show_in(self):
        try:
            return self.keyfile.get_string(GROUP, 'OnlyShowIn')
        except:
            return ''

    @show_in.setter
    def show_in(self, ashow_in):
        if ashow_in in  ['', ';']:
            self.remove_key('OnlyShowIn')
        else:
            self.keyfile.set_string(GROUP, 'OnlyShowIn', ashow_in)
        self.dirty_flag = True

    @property
    def categories(self):
        try:
            return self.keyfile.get_string(GROUP, 'Categories')
        except:
            return ''

    @categories.setter
    def categories(self, acategories):
        if acategories == '':
            self.remove_key('Categories')
        else:
            self.keyfile.set_string(GROUP, 'Categories', acategories)
        self.dirty_flag = True

    @property
    def comment(self):
        try:
            return self.keyfile.get_string(GROUP, 'Comment')
        except:
            return ''

    @comment.setter
    def comment(self, acomment):
        if acomment == '':
            self.remove_key('Comment')
        else:
            self.keyfile.set_string(GROUP, 'Comment', acomment)
        self.dirty_flag = True

    @property
    def mime_type(self):
        try:
            return self.keyfile.get_string(GROUP, 'MimeType')
        except:
            return ''

    @mime_type.setter
    def mime_type(self, amime_type):
        if amime_type in ['', ';']:
            self.remove_key('MimeType')
        else:
            self.keyfile.set_string(GROUP, 'MimeType', amime_type)
        self.dirty_flag = True


    @property
    def wm_class(self):
        try:
            return self.keyfile.get_string(GROUP, 'StartupWMClass')
        except:
            return ''

    @wm_class.setter
    def wm_class(self, awm_class):
        if awm_class == '':
            self.remove_key('StartupWMClass')
        else:
            self.keyfile.set_string(GROUP, 'StartupWMClass', awm_class)
        self.dirty_flag = True


    @property
    def run_in_terminal(self):
        try:
            return self.keyfile.get_boolean(GROUP, 'Terminal')
        except:
            return False

    @run_in_terminal.setter
    def run_in_terminal(self, arun_in_terminal):
        self.keyfile.set_boolean(GROUP, 'Terminal', arun_in_terminal)
        self.dirty_flag = True

    
    @property
    def hidden(self):
        try:
            return self.keyfile.get_boolean(GROUP, 'Hidden')
        except:
            return False

    @hidden.setter
    def hidden(self, ahidden):
        self.keyfile.set_boolean(GROUP, 'Hidden', ahidden)
        self.dirty_flag = True


    @property
    def quicklist(self):
        result = []
        groups, _ = self.keyfile.get_groups()
        for group in groups:
            if group.endswith(AYATANA_GROUP_SUFFIX):
                try:
                    command =  self.keyfile.get_string(group, 'Exec')
                except:
                    command = ''
                try:
                    title = self.keyfile.get_string(group, 'Name')
                except:
                    title = command
                result.append((title, command))
        return result

    @quicklist.setter
    def quicklist(self, alist):
        shortcuts = []
        groups, _ = self.keyfile.get_groups()
        for group in groups:
            if group.endswith(AYATANA_GROUP_SUFFIX):
                self.keyfile.remove_group(group)
        for i, row in enumerate(alist):
            title, command = row[0], row[1]
            group_name = 'Group%s' % i
            shortcuts.append(group_name)
            group = group_name + AYATANA_GROUP_SUFFIX
            self.keyfile.set_string(group, 'Exec', command)
            self.keyfile.set_string(group, 'Name', title)
        if shortcuts:            
            key = 'X-Ayatana-Desktop-Shortcuts'
            value = ';'.join(shortcuts)
            self.keyfile.set_string(GROUP, key, value)


    def set_from_dict(self, data):
        print data
        self.type = data['type'] # needs to be set first
        for key, value in data.iteritems():
            setattr(self, key, value)

    def get_as_dict(self):
        fields = (
            'type', 'title', 'command', 'working_dir', 'run_in_terminal',
            'hidden', 'icon', 'keywords', 'categories', 'wm_class', 
            'comment', 'mime_type', 'show_in', 'quicklist'
            )
        data = {}
        for f in fields:
            data[f] = getattr(self, f)
        return data

    def is_dirty(self, data):
        if self.dirty_flag:
            return True
        for key, value in data.iteritems():
            if getattr(self, key) != value:
                return True
        else:
            return False

    def load(self, path):
        try:
            self.keyfile.load_from_file(
                path,
                GLib.KeyFileFlags.KEEP_COMMENTS | 
                GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except Exception, e:
            return str(e)
        self.dirty_flag = False


    def save(self, path): 
        content = self.keyfile.to_data()[0]
        try:
            os.rename(path, '%s~' % path)
        except Exception, e:
            print e
        try:
            with open(path, 'w') as _file:
                _file.write(content)
            mode = os.stat(path).st_mode
            os.chmod(path, mode | stat.S_IEXEC)
        except Exception, e:
           return str(e)
        self.dirty_flag = False
        return None


