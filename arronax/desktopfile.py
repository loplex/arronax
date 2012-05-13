#!/usr/bin/env python

#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio, GLib




class DesktopFile(object):

    def __init__(self, path=None):
        if path is not None:
            self.keyfile = GLib.KeyFile.load_from_file(path,
                                                       GLib.KeyFileFlags.KEEP_COMMENTS | 
                                                       GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        else:
            self.keyfile = GLib.KeyFile() 
        
        self.path = path
        self.group = 'Desktop Entry'


    def get_from_key(self, key):
        return self.keyfile.get_value(self.group, key)
        

    def set_to_key(self, key, value):
        if isinstance(value, bool):
            s = str(value).lower()
        else:
            s = str(value)
        if value == '':
            self.keyfile.remove_key(self.group, key)
        else:
            self.keyfile.set_value(self.group, key, s)

    def save(self, path):
        print self.keyfile.to_data()

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

        
    
