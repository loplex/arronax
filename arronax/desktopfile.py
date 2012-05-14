#!/usr/bin/env python

#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio, GLib
from gettext import gettext as _

import os.path

import dialogs

class DesktopFile(object):

    def __init__(self, win, path=None):
        self.win = win
        self.keyfile = GLib.KeyFile() 
        if path is not None:
            try:
                self.keyfile.load_from_file(path,
                                            GLib.KeyFileFlags.KEEP_COMMENTS | 
                                            GLib.KeyFileFlags.KEEP_TRANSLATIONS)
            except Exception, e:
                print e
        
        self.path = path
        self.group = 'Desktop Entry'
        self['Type'] = 'Application'
        self['Version'] = '1.0'


    def get_from_key(self, key):
        try:
            return self.keyfile.get_value(self.group, key)
        except Exception, e:
            return ''
        

    def set_to_key(self, key, value):
        if isinstance(value, bool):
            s = str(value).lower()
        else:
            s = str(value)
        if value == '':
            self.keyfile.remove_key(self.group, key)
        else:
            self.keyfile.set_value(self.group, key, s)


    def check_data(self, filename):
        msg=''
        # if self['Name'] == '':
        #     msg = '%s\n%s' % (msg, _("You neede to provide a name."))
        if filename.strip() == '':
            msg = '%s\n%s' % (msg, _("You neede to provide a file name."))
        if self['Exec'] == '':
            msg = '%s\n%s' % (msg, _("You neede to provide a command."))
        return msg

    def check_filename(self, filename):
        if filename == '':
            return None
        path = os.path.abspath(filename)
        if not path.endswith('.desktop'):
            if dialogs.yes_no_question(self.win, _("Append '.desktop'?"),
                                       _("The file name doesn't end with '.desktop'.\n Should I add it?")) == Gtk.ResponseType.YES:
                path = '%s.desktop' % path  
        return path
        
    def save(self, path):
        msg = self.check_data(path)
        if msg != '':
            dialogs.error(self.win, _('Error'), msg)
            return

        path = self.check_filename(path)
        
        content = self.keyfile.to_data()[0]
        try:
            with open(path, 'w') as _file:
                _file.write(content)
        except Exception, e:
           dialogs.error(self.win, _('Error'), str(e))


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

        
    
