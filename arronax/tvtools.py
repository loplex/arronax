# -*- coding: utf-8 -*-
# Fernweh - Put things on a map
# https://florian-diesch.de/software/fernweh/
#
# Copyright (C) 2017 Florian Diesch devel@florian-diesch.de
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


from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio


def _getattr_try_call(obj, attr):
    if obj is None:
        return '???'
    data = getattr(obj, attr)
    try:
        return data()
    except TypeError:
        return data

def make_cell_data_func(attr, column=0, cell_prop='text'):
    def func(tree_column, cell, tree_model, iter, data):
        obj = tree_model[iter][column]
        data = _getattr_try_call(obj, attr)
        cell.set_property(cell_prop, data)
    return func


def make_sort_func(attr, column=0, cmp_func=None):
    if cmp_func is None:
        cmp_func = lambda a,b: True if a is None or b is None else (a > b) - (a < b)

    def func(model, a, b, data):
        obj_a = model[a][column]
        obj_b = model[b][column]
        return cmp_func(_getattr_try_call(obj_a, attr),
                        _getattr_try_call(obj_b, attr))
    return func


def add_cell_renderer(control, col_no=0, renderer=None, attr='text'):
    if renderer is None:
        renderer=Gtk.CellRendererText()
    control.pack_start(renderer, True)
    if attr is not None:        
        control.add_attribute(renderer, attr, col_no)
    return renderer
    

def create_treeview_column(widget, title, col_no, renderer=None,
                           attr='text', activatable=False, sort_id=None,
                           is_sort_col=False, resizable=True,
                           reorderable=True, min_width=-1, max_width=-1,
                           obj_attr=None):
    model = widget.get_model()
    if isinstance(model, Gtk.TreeModelFilter):
        model = model.get_model()
    column = Gtk.TreeViewColumn(title)
    widget.append_column(column)

    if sort_id is None:
        sort_id = col_no
        
    column.set_resizable(resizable)
    column.set_reorderable(reorderable)
    column.set_min_width(min_width)
    column.set_max_width(max_width)

    renderer = add_cell_renderer(column, col_no, renderer,
                                 attr if obj_attr is None else None)
    if activatable:
        renderer.set_activatable(True)
        
    if obj_attr is not None:
        column.set_cell_data_func(renderer,
                                  make_cell_data_func(obj_attr,
                                                      cell_prop=attr))
        if model:
            model.set_sort_func(
                sort_id, make_sort_func(obj_attr))
    
    column.set_sort_column_id(sort_id)


    if is_sort_col:
        if model:
            model.set_sort_column_id(sort_id, Gtk.SortType.ASCENDING)
    return column, renderer


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

        
def del_current_row(treeview):
    path, column = treeview.get_cursor()
    if path is not None:
        model = treeview.get_model()
        del model[path]

        
def move_down_current_row(treeview):
    path, column = treeview.get_cursor()
    if path is not None:
        model = treeview.get_model()
        aiter = model.get_iter(path)
        try:
            next(path)
            dest = model.get_iter(path)
            model.move_after(aiter, dest)
        except ValueError:
            pass
    
def move_up_current_row(treeview):
    path, column = treeview.get_cursor()
    if path is not None:
        model = treeview.get_model()
        aiter = model.get_iter(path)
        try:
            path.prev()
            dest = model.get_iter(path)
            model.move_before(aiter, dest)
        except ValueError:
            pass

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
                
def row_changed(tv, row):
       path = row.path
       model = tv.get_model()
       iter = model.get_iter(path)
       model.row_changed(path, iter)

       
def append_row(treeview, row):
    model = treeview.get_model()
    iter_ = model.append(row)
    path = model.get_path(iter_)
    treeview.set_cursor(path)
