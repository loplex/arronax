.. -*- coding: utf-8 -*-

==================
 What is Arronax?
==================

Arronax is a program to create and modify starters (technically:
.desktop files) for applications and locations (URLs).

Arronax can be used as a standalone application or as a plugin for
Caja (default file manager of the MATE desktop environment)
Nautilus (default file manager of the Gnome and Unity desktop
environments)  and Nemo (default file manager of the Cinnamon desktop environment).  

Arronax as file manager extension
=============================

As file manager plugin Arronax adds a menu item “Create starter for this
file” or “Create a starter for this program” to the context menu
(that’s the menu you get when you right-click a file in the file
manager). If the file is a application starter you get an item “Modify
this starter” instead.

If you have icons on your desktop enabled Arronax adds a menu item
“Create starter” to your desktop’s context menu.  

Arronax as standalone application
=================================

Arronax as standalone application can be started just like any other
application using the application menu or application search function
of your desktop environment.  

Drag & Drop
===========

Arronax supports Drag&Drop:

* You can drag an application icon and drop it on an open Arronax
  window. Don’t drop it on one of the input fields in the Arronax
  window but on the free space beneath the icon.

* You can drag files from the file manager and other applications and
  drop them on the input area in the “MIME types” tab to add the
  corresponding MIME types to the list. This will add every MIME type
  only once, even if you add multiple files with the same MIME type.

* You can drag image files from the file manager or other applications
  and drop them on the icon selector at the left of the Arronax window
  to use that image as icon for the starter. It is up to you tom take
  care that the image has the right size.

* You can drag a file or folder from the file manager or a URL from
  your web browser and drop it on the “Command”, “Start in Folder” or
  “File or URL” input area to use the corresponding file path.


========
 Status
========


As far as I know there aren’t any serious bugs in Arronax.

If you find a bug in Arronax please report it at the bugtracker at
Launchpad so that I can fix it. Thank you.  


==============
 Requirements 
==============

Arronax is beeing developed and tested on Ubuntu.

Arronax needs:

* Gtk 3.x
* Python 2.7
* PyGObject
* distribute

The Caja plugin needs:

* Caja
* Python binding for Caja
* GObject introspection data for Caja

The Nautilus plugin needs:

* Nautilus
* Python binding for Nautilus
* GObject introspection data for Nautilus

The Nemo plugin needs:

* Nemo
* Python binding for Nemo
* GObject introspection data for Nemo




If you install the .deb package this packages will be automatically
installed if needed.  

Enable icons on your desktop
============================

With Gnome Nautilus is by default configured not to show icons on your
desktop. You can change that by opening a Terminal, type::

    gsettings set org.gnome.desktop.background show-desktop-icons true


=======================
 Where can you get it?
=======================

Arronax is available from

    http://www.florian-diesch.de/software/arronax/


=========
 License
=========

You can use Arronax under the conditions of GPL v3 or later.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/
