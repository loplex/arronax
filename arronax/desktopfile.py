#!/usr/bin/env python

#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio, GLib
from gettext import gettext as _

import os, os.path, stat, logging

from . import dialogs

GROUP = 'Desktop Entry'
#ACTION_TEMPLATE = ' Shortcut Group'
ACTION_PREFIX = 'Desktop Action '

class DesktopFile(object):

    def __init__(self):
        self.keyfile = GLib.KeyFile()
        self.dirty_flag = False

    def has_key(self, group, key):
        try:
            value = self.keyfile.get_string(group, key)
            return value is not None
        except:
            return False
        
    def remove_key(self, group, key):
        try:
            if self.has_key(group, key):
                self.keyfile.remove_key(group, key)
        except Exception as e:
            logging.error('rm key: {}'.format(e))
            

    def get_string(self, group, key, default):
        if self.has_key(group, key):
            return self.keyfile.get_string(group, key)
        else:
            return default

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
            self.remove_key(GROUP, 'Name')
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
        if self.type == 0:
            self.remove_key(GROUP, 'URL')
            self.keyfile.set_string(GROUP, 'Exec', acommand)
        else:
            self.remove_key(GROUP, 'Exec')
            self.keyfile.set_string(GROUP, 'URL', acommand)
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
            self.remove_key(GROUP, 'Path')
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
            self.remove_key(GROUP, 'Icon')
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
            self.remove_key(GROUP, 'Keywords')
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
            self.remove_key(GROUP, 'OnlyShowIn')
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
            self.remove_key(GROUP, 'Categories')
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
            self.remove_key(GROUP, 'Comment')
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
            self.remove_key(GROUP, 'MimeType')
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
            self.remove_key(GROUP, 'StartupWMClass')
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
        actions =  self.get_string(GROUP, 'Actions', '')
        for gname in actions.split(';'):
            if gname:                
                group = ACTION_PREFIX + gname
                command = self.get_string(group, 'Exec', '')
                title = self.get_string(group, 'Name', command)
                result.append((title, command, gname))
        return result

    def create_group_name(self, title):
        basename = ''.join(c for c in title if c.isalpha())
        if basename == '':
            basename = '0'
        name = basename
        cnt = 1
        while self.keyfile.has_group(ACTION_PREFIX + name):
            name = '%s%s' %(basename, cnt)
            cnt+=1
        return name

    @quicklist.setter
    def quicklist(self, alist):
        _oldgrps = self.get_string(GROUP, 'Actions', '')
        oldgroups = set(i for i in _oldgrps.split(';') if i)
        groups = []
        for title, command, gname in alist:
            if gname == '':
                gname = self.create_group_name(title)
            group = ACTION_PREFIX + gname
            self.keyfile.set_string(group, 'Exec', command)
            self.keyfile.set_string(group, 'Name', title)
            groups.append(gname)
            self.dirty_flag = True

        if groups:
            value = ';'.join(groups)
            value = value + ';'
            self.keyfile.set_string(GROUP, 'Actions', value)            
        else:
            self.remove_key(GROUP, 'Actions')
        for gname in oldgroups - set(groups):
            group = ACTION_PREFIX + gname
            if self.keyfile.has_group(group):
                self.keyfile.remove_group(group)
                self.dirty_flag = True


    def set_from_dict(self, data):
        self.type = data['type'] # needs to be set first
        for key, value in data.items():
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
        logging.debug('dirty: flag:{}  data:{}'.format(
            self.dirty_flag, data))
        if self.dirty_flag:
            return True
        list_fields = set(('keywords', 'categories', 'mime_type', 
                           'show_in'))
        for key, value in data.items():
            my_value = getattr(self, key)
            if key in list_fields:
                value = str(value).rstrip(';')
                my_value = str(my_value).rstrip(';')
            if my_value != value:
                logging.debug('dirty: {}: "{}" != "{}"'.format(
                    key, value, my_value))
                return True
        else:
            return False


    def clear(self):
        self.type = 0
        self.title = ''
        self.command = ''
        self.working_dir = ''
        self.run_in_terminal = False
        self.hidden = False
        self.icon = ''
        self.keywords = ''
        self.categories = ''
        self.wm_class = ''
        self.comment = ''
        self.mime_type = ''
        self.show_in = ''
        self.quicklist = []
        self.dirty_flag = False

    def load(self, path):
        try:
            self.keyfile.load_from_file(
                path,
                GLib.KeyFileFlags.KEEP_COMMENTS | 
                GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except Exception as e:
            return str(e)
        self.dirty_flag = False


    def save(self, path): 
        content = self.keyfile.to_data()[0]

        try:
            if os.path.exists(path):
                os.rename(path, '%s~' % path)
        except Exception as e:
            logging.error('os.rename: p:{} e:{}'.format(path, e))
        try:
            with open(path, 'w') as _file:
                _file.write(content)
            self.dirty_flag = False
            mode = os.stat(path).st_mode
            os.chmod(path, mode | stat.S_IEXEC)
        except Exception as e:
           return str(e)
        return None


