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

from gi.repository import GLib
import os.path


XDG_DATA_HOME = GLib.get_user_data_dir()
XDG_CONFIG_HOME = GLib.get_user_config_dir()
XDG_CACHE_HOME = GLib.get_user_cache_dir()
XDG_RUNTIME_DIR = GLib.get_user_runtime_dir()
XDG_CONFIG_DIRS = GLib.get_system_config_dirs()
XDG_DATA_DIRS = GLib.get_system_data_dirs()


def get_user_dir(name, default):
    name = 'DIRECTORY_{}'.format(name.upper())
    id = getattr(GLib.UserDirectory, name, None)
    dir = GLib.get_user_special_dir(id)
    if dir is None:
        return os.path.expanduser(default)
    else:
        return dir

