#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

import argparse, logging, enum

from arronax import settings


class StarterType(enum.Enum):
    Link = 1
    Application = 2


def setup_logging(args):
    if args.loglevel == 'debug':
        format='%(levelname)s %(filename)s:%(funcName)s:L%(lineno)d:: %(message)s'
    else:
        format='%(message)s'
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper()),
        format=format,
        filename=args.logfile
    )


def parse_cli_args():
    common = argparse.ArgumentParser(
        add_help=False)
    _loglevels = ['debug', 'info', 'warn', 'error', 'critical']
    common.add_argument('--loglevel', choices=_loglevels, default='warn')
    common.add_argument('--logfile', default=None)

    parser = argparse.ArgumentParser(
        description='Create and modify .desktop files',
        prog=settings.app_name, parents=[common],
        allow_abbrev=False)
    parser.add_argument('--version', action='version',
          version='{} {}'.format(settings.APP_TITLE, settings.APP_VERSION))
    parser.add_argument('--dir', '-d')

    typeargs = parser.add_mutually_exclusive_group()
    typeargs.add_argument('--link', '-l', default=None,
        const=StarterType.Link, action='store_const', dest='stype')
    typeargs.add_argument('--application', '-a', default=None,
        const=StarterType.Application, action='store_const', dest='stype')
    
    parser.add_argument('path', nargs='?', default=None)
    
    args = parser.parse_args()

    setup_logging(args)
    
    logging.debug('ARGS: {}'.format(args))
    return args

