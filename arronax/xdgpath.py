#!/usr/bin/env python
#-*- coding: utf-8-*-

import os.path
import xdg.BaseDirectory


USER_DIR_DEFAULTS = '/etc/xdg/user-dirs.defaults'
USER_DIR_CONFIG = os.path.join(xdg.BaseDirectory.xdg_config_home, 
                               'user-dirs.dirs')

def _read_user_dir_defaults(path):
    result = {}
    try:
        with open (path) as input:
            for line in input:
                line = line.strip()
                if not line.startswith('#'):
                    key, value = line.split('=', 1)

                    value = value.strip()
                    value = os.path.join(os.path.expanduser('~/'), value)

                    key = key.strip().lower()
                    
                    result[key] = value
    except IOError:
        pass
    return result


def _read_user_dirs_home(path):
    result = {}
    try:
        with open (path) as input:
            for line in input:
                line = line.strip()
                if line.startswith('XDG_'):
                    key, value = line.split('=', 1)

                    value = value.replace('"','').replace('$HOME', '~')
                    value = os.path.expanduser(value)

                    key = key[4:-4].lower()
                    
                    result[key.strip()] = value.strip()                
    except IOError:
        pass
    return result


def _get_user_dirs():
    dirs = _read_user_dir_defaults(USER_DIR_DEFAULTS)
    dirs.update(_read_user_dirs_home(USER_DIR_CONFIG))
    return dirs

def get_user_dir(name, default):
    dirs = _get_user_dirs()
    return dirs.get(name, default)
    
    


if __name__ == '__main__':
    print(_get_user_dirs())
    print('DESKTOP:', get_user_dir('desktop', os.path.expanduser('~/Desktop')))
    print('FOO:', get_user_dir('foo', os.path.expanduser('~/bar')))


