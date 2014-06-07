#-*- coding: utf-8 -*-
#
# Copyright (C) 2014 Florian Diesch <devel@florian-diesch.de>
#
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



from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, Pango


def add_cell_renderer(control, col_no=0, renderer=None, attr='text'):
    if renderer is None:
        renderer=Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        renderer.set_property('ellipsize-set', True)
    control.pack_start(renderer, True)
    control.add_attribute(renderer, attr, col_no)
    

def create_treeview_column(widget, title, col_no, renderer=None,
                           attr='text', activatable=False,
                           sort_column=-1):
    column = Gtk.TreeViewColumn(title)
    column.set_sort_column_id(sort_column)
    column.set_resizable(True)
    widget.append_column(column)
    if activatable:
        renderer.set_activatable(True)
    add_cell_renderer(column, col_no, renderer,  attr)


def move_current_row_up(treeview):
    path, column = treeview.get_cursor()
    model = treeview.get_model()
    aiter = model.get_iter(path)
    biter = model.iter_previous(aiter)
    if biter:
        model.swap(aiter, biter)

def move_current_row_down(treeview):
    path, column = treeview.get_cursor()
    model = treeview.get_model()
    aiter = model.get_iter(path)
    biter = model.iter_next(aiter)
    if biter:
        model.swap(aiter, biter)

def get_current_row(treeview):
    path, column = treeview.get_cursor()
    if path is not None:
        model = treeview.get_model()
        return model[path]

def set_current_row(treeview, row):
    path, column = treeview.get_cursor()    
    if path is None:
        append_row(treeview, row)
    else:
        model = treeview.get_model()
        model[path]=row

def insert_row_after_current(treeview, row):
    path, column = treeview.get_cursor()    
    if path is None:
        append_row(treeview, row)
    else:
        model = treeview.get_model()
        aiter = model.get_iter(path)
        biter = model.insert_after(aiter, row)
        if biter is not None:
            path = model.get_path(biter)
            treeview.set_cursor(path)
        
    

def del_current_row(treeview):
    path, column = treeview.get_cursor()
    if path is not None:
        model = treeview.get_model()
        del model[path]

def append_row(treeview, row):
    model = treeview.get_model()
    iter_ = model.append(row)
    path = model.get_path(iter_)
    treeview.set_cursor(path)
