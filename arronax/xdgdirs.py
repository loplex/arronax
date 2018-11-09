# -*- coding: utf-8 -*-
#
# Arronax - a application and filemananer plugin to create and modify .desktop files
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

import os, os.path


def _get_env_var(name, default=''):
    path = os.environ.get(name, default)
    if path == '':
        return default
    else:
        return path

def _user_path(*dirs):
    path = os.path.join('~', *dirs)
    return os.path.expanduser(path)


XDG_DATA_HOME   = _get_env_var('XDG_DATA_HOME',
                               _user_path('.local', 'share'))
XDG_CONFIG_HOME = _get_env_var('XDG_CONFIG_HOME',
                               _user_path('.config'))
XDG_DATA_DIRS   = _get_env_var('XDG_DATA_DIRS',
                               ' /usr/local/share/:/usr/share/')
XDG_CONFIG_DIRS = _get_env_var('XDG_CONFIG_DIRS',
                               '/etc/xdg')
XDG_CACHE_HOME  = _get_env_var('XDG_CACHE_HOME',
                               _user_path('.cache'))
XDG_RUNTIME_DIR = _get_env_var('XDG_RUNTIME_DIR',
                               None)

USERDIR_DEFAULTS = '/etc/xdg/user-dirs.defaults'
USERDIR_CONFIG = os.path.join(XDG_CONFIG_HOME, 'user-dirs.dirs')

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
    dirs = _read_user_dir_defaults(USERDIR_DEFAULTS)
    dirs.update(_read_user_dirs_home(USERDIR_CONFIG))
    return dirs

def get_user_dir(name, default):
    dirs = _get_user_dirs()
    return dirs.get(name, default)


