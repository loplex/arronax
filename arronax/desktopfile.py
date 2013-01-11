#!/usr/bin/env python

#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio, GLib
from gettext import gettext as _

import os, os.path, stat

import dialogs

FIELD_NOT_USED=object()

class KeyNotSetException(Exception):
    pass

class DesktopFile(object):

    def __init__(self, win):
        self.win = win
        self.keyfile = GLib.KeyFile()
        self.types = {}
        self.load(None)


    def load(self, path):
        self.path = path
        self.group = 'Desktop Entry'
        self['Version'] = '1.0'

        if path is not None:
            try:
                self.keyfile.load_from_file(path,
                                            GLib.KeyFileFlags.KEEP_COMMENTS | 
                                            GLib.KeyFileFlags.KEEP_TRANSLATIONS)
            except Exception, e:
                return str(e)
                
        if self['Type'] not in ('', 'Application', 'Link'):
            return _("Arronax doesn't support this kind of starter yet")
        if self['Type'] == '':   ## Do we really need this?
            self['Type'] = 'Application'
        return None


    def set_type_for_key(self, key, type):
        self.types[key] = type

    def has_key(self, key):
        return key in self.keyfile.get_keys(self.group)

    def get_from_key(self, key):
        try:
            if self.types.get(key, str) == bool:
                return self.keyfile.get_boolean(self.group, key) 
            else:
                return self.keyfile.get_value(self.group, key)
        except Exception, e:
            if self.types.get(key, str) == bool:
                return False
            else:
                return ''
        

    def set_to_key(self, key, value):
        if value in ('', FIELD_NOT_USED):
            self.keyfile.remove_key(self.group, key)
        else:
            if self.types.get(key, str) == bool:
                self.keyfile.set_boolean(self.group, key, value)
            else:
                self.keyfile.set_string(self.group, key, str(value))
                                


 
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

        return None


    def __getitem__(self, key):
        return self.get_from_key(key)

    def __setitem__(self, key, value):
        self.set_to_key(key, value)
                


if __name__ == '__main__':
    df = DesktopFile()
    df['Name'] = 'Foo'
    df['Hidden'] = True

    print df['Name'],  df['Hidden']
    df.save('foo')

        
    
