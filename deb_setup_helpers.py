# Copyright (C) 2012 by Florian Diesch <devel@florian-diesch.de>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path, re

DEB_VERSION_FULL_RE = re.compile(r'^[^ ].*\((?P<version>[a-z0-9:.-_]*)\)')
DEB_VERSION_SHORT_RE = re.compile(r'^[^ ].*\((?P<version>[0-9.-]*)[^)]*\)')

DEB_DESCRIPTION_RE = re.compile(r'^Description: (?P<description>.*)')

def get_deb_version(changelog=None, full=False):
    if changelog is None:
        changelog = os.path.join('debian', 'changelog')
    if full:
        regex = DEB_VERSION_FULL_RE
    else:
        regex = DEB_VERSION_SHORT_RE

    with open(changelog) as f:
         for line in f:
             match = regex.search(line)
             if match:
                 print 'VERSION',  match.group('version')
                 return match.group('version')
    raise AssertionError('No version found in %s' % changelog)


def get_deb_description(control=None):
     if control is None:
        control = os.path.join('debian', 'control')
       
     regex = DEB_DESCRIPTION_RE
     
     with open(control) as f:
         for line in f:
             match = regex.search(line)
             if match:
                 print 'DESC',  match.group('description')
                 return match.group('description')
     raise AssertionError('No description found in %s' % control)

    
    

