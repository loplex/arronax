#
# Unsettings - a configuration frontend for the Unity desktop environment
#
# Copyright (C) 2012 Florian Diesch <devel@florian-diesch.de>
#
# Homepage: http://www.florian-diesch.de/software/unsettings/
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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import os.path
import settings

_WIDGET_REGISTRY = {}
_DEFAULTER_REGISTRY = {}
_WATCHER_REGISTRY = {}


RAW = object()

STANDARD_DEFAULT = object()

class DefaulterMeta(type):
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        wraps = getattr(cls, '__wraps__', ())
        for w in wraps:
            _DEFAULTER_REGISTRY[w] = cls


class DefaulterBase(object):
    __metaclass__ = DefaulterMeta
    __default__ = None  
    __wraps__ = (Gtk.TreeView, Gtk.IconView, Gtk.Grid, Gtk.Button)

    def __init__(self, value=STANDARD_DEFAULT):
        if value == STANDARD_DEFAULT:
            self.default = self.__default__
        else:
            self.default = value

    def get_default(self):
        return self.default

    def set_default(self, value):
        self.default = value
    

class FloatDefaulter(DefaulterBase):
    __default__ = 0.0
    __wraps__ =  (Gtk.Scale, Gtk.HScale, Gtk.VScale, Gtk.SpinButton)

class IntDefaulter(DefaulterBase):
    __default__ = 0
    __wraps__ =  (Gtk.ComboBox,)

class StringDefaulter(DefaulterBase):
    __default__ = ''
    __wraps__ = (Gtk.Label, Gtk.Entry, Gtk.TextView, Gtk.Image,)

class BooleDefaulter(DefaulterBase):
    __default__ = False
    __wraps__ = (Gtk.ToggleButton, Gtk.CheckButton, 
                 Gtk.ComboBoxText, Gtk.Switch)

class ListDefaulter(DefaulterBase):
    __default__ = []
    __wraps__ = ()



class WatcherMeta(type):
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        wraps = getattr(cls, '__wraps__', ())
        for w in wraps:
            _WATCHER_REGISTRY[w] = cls


class WatcherBase(object):
   __metaclass__ = WatcherMeta
   __wraps__ = (Gtk.Grid,)

   __widget_signal__ = None

   def __init__(self, widget, connection_groups, tags, converter=None):
       self.widget = widget
       self.cgroups = connection_groups
       self.connect_to_widget()
       self.tags = tags

       if converter is None:
           self.converter_func = lambda x: x
       elif isinstance(converter, dict):
           self.converter_func = lambda x: converter.get(x)
       elif callable(converter):
           self.converter_func = converter
       else:
           self.converter_func = lambda x: converter
             
   def action(self, *args):
       data = self.widget.get_data()
       value = self.converter_func(data)
       for cgroup in  self.cgroups:
           cgroup.switch(self.tags, value)

   def connect_to_widget(self):
       if self.__widget_signal__ is not None:
           self.widget.widget.connect(self.__widget_signal__, self.action)
       

class ChangedWatcher(WatcherBase):
    __widget_signal__ = 'changed'
    __wraps__ = (Gtk.ComboBox, Gtk.ComboBoxText)
        
        

def get_watcher(widget, *args, **kwargs):
    klass = _WATCHER_REGISTRY.get(type(widget.widget), None)
    if klass is not None:
        return klass(widget=widget, *args, **kwargs)
    
    

class WidgetMeta(type):
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        wraps = getattr(cls, '__wraps__', ())
        for w in wraps:
            _WIDGET_REGISTRY[w] = cls


class WidgetBase(object):
    __metaclass__ = WidgetMeta
    __wraps__ = (Gtk.Grid, Gtk.Button)

    def __init__(self, widget, defaulter):
        self.widget = widget
        self.defaulter = defaulter

    def get_data(self):
        pass
    
    def set_data(self, data):
        pass

    def hide(self):
        self.widget.hide()

    def show(self):
        self.widget.show_all()

    def activate(self, value):
        self.widget.set_sensitive(value)
        
        
    def get_default_value(self):
        return self.defaulter.get_default()

    def set_default_value(self, value):
        self.defaulter.set_default(value)

    def clear(self):
        self.set_data(self.get_default_value())
    

class NotebookPageWidget(WidgetBase):
    __wraps__ = ()

    def __init__(self, widget, defaulter, page_num):
        widget = widget.get_nth_page(page_num)
        WidgetBase.__init__(self, widget, defaulter)
 

class ValueWidget(WidgetBase):
    """ widget that has get_value() and set_value() methods
    """
    __wraps__ = (Gtk.Scale, Gtk.HScale, Gtk.VScale, Gtk.SpinButton)

    def set_data(self, value):
        self.widget.set_value(value)


    def get_data(self):
        return self.widget.get_value()



class TextWidget(WidgetBase):
    """ widget that has get_text() and set_text() methods
    """
    __wraps__ = (Gtk.Label, Gtk.Entry)

 
    def set_data(self, value):
        self.widget.set_text(value)


    def get_data(self):
        return self.widget.get_text()

class TextBufferWidget(WidgetBase):
    """ widget that has a buffer field with get_text() and set_text() methods
    """
    __wraps__ = (Gtk.TextView,)

 
    def set_data(self, value):
        buffer =  self.widget.get_buffer()
        buffer.set_text(value)


    def get_data(self):
        buffer =  self.widget.get_buffer()
        return buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(), False)


class ActiveWidget(WidgetBase):
    """ widget that has get_active() and set_active() methods
    """
    __wraps__ = (Gtk.ToggleButton, Gtk.CheckButton, 
                 Gtk.ComboBoxText, Gtk.Switch)

    def set_data(self, value):
        self.widget.set_active(value)


    def get_data(self):
        return self.widget.get_active()

class ActiveIDWidget(WidgetBase):
    """ widget that has get_active_id() and set_active_id() methods
    """
    __wraps__ = (Gtk.ComboBox,)

    def set_data(self, value):
        self.widget.set_active_id(value)

    def get_data(self):
        return self.widget.get_active_id()


class ListWidget(WidgetBase):
    """ widget that has get_list() and set_list() methods
    """
    __wraps__ = ()
    
    def set_data(self, value):
        if value is not None:
            self.widget.set_list(value)
        
    def get_data(self):
        return self.widget.get_list()


class SelectionListWidget(WidgetBase):
    __wraps__ = ()


    def _add_cell_renderer(self, control, col_no=0, renderer=None, attr='text'):
        if renderer is None:
            renderer=Gtk.CellRendererText()
        control.pack_start(renderer, True)
        control.add_attribute(renderer, attr, col_no)
    

    def _create_treeview_column(self, widget, title, col_no=0, renderer=None,
                           attr='text'):
        column = Gtk.TreeViewColumn(title)
        widget.append_column(column)
        self._add_cell_renderer(column, col_no, renderer,  attr)

    def _toggle_value(self, path):
        model = self.widget.get_model()
        if model is None:
            return
        _iter = model.get_iter(path)
        model[_iter][0] = not model[_iter][0]

    def __init__(self, widget, defaulter, items):
        WidgetBase.__init__(self, widget, defaulter)

        ## columns: 'enabled?', 'value to save', 'value to display'
        model = Gtk.ListStore(bool,  str, str)
        
        # sort by displayed value
        model.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        widget.set_model(model)

        crt = Gtk.CellRendererToggle()
        crt.connect('toggled', lambda w,p: self._toggle_value(p))
        self._create_treeview_column(widget, 'Enabled', 0,
                                     renderer=crt,
                                     attr='active')
        self._create_treeview_column(widget, 'Environment', 2)

        defaults = None
        # fill model and set defaults
        if isinstance(items, dict):
            for k,v in items.iteritems():
                model.append([True, k, v])
            defaults = items.keys()
        else:
            for i in items:
                model.append([True, i, i])
                defaults = items
        self.defaulter.set_default(defaults)

    def get_data(self):        
        model = self.widget.get_model()
        if model is None:
            return ''
        all_set = all([i[0]  for i in model])

        if all_set:
            return []
        else:
            items = [i[2] for i in model if i[0]]
            return items
            

    def set_data(self, value):
        model = self.widget.get_model()
        if model is None or value is None:
            return
        items = value
        for row in model:
            row[0] = row[1] in items or not value
        self.widget.set_model(model)                     

class ModelWidget(WidgetBase):
    """ widget that has get_model() and set_model() methods
    """
    __wraps__ =  (Gtk.TreeView, Gtk.IconView)
    
    def set_data(self, value):
        if value is not None:
            self.widget.set_model(value)
        
    def get_data(self):
        return self.widget.get_model()


class FontNameWidget(WidgetBase):
    """ widget that has get_font_name() and set_font_name() methods
    """
    __wraps__ =  (Gtk.FontButton,)
    
    def set_data(self, value):
        if value is not None:
            self.widget.set_font_name(value)
        
    def get_data(self):
        return self.widget.get_font_name()

class ColorChooserWidget(WidgetBase):
    """ widget that implements Gtk.ColorChooser
    """
    __wraps__ =  (Gtk.ColorButton,)
    
    def set_data(self, value):        
        if value is not None:
            rgba = self.widget.get_rgba()
            rgba.parse(value)
        
    def get_data(self):
        rgba = self.widget.get_rgba()
        s = '#%02x%02x%02x' % (rgba.red*255,
                               rgba.green*255,
                               rgba.blue*255)
        return s

class FileOrIconNamePropertyWidget(WidgetBase):
    """ widget that has a "file" property
    """
    __wraps__ = (Gtk.Image,)


    def _search_icon(self, icon):
        nx_icon = os.path.splitext(icon)[0]
        icon_theme = Gtk.IconTheme.get_for_screen(self.widget.get_screen())
           
        if (icon_theme.has_icon(nx_icon)):
            return icon_theme.lookup_icon(nx_icon, 
                                          settings.DEFAULT_ICON_SIZE,
                                          0).get_filename()
        else:
            return settings.DEFAULT_ICON        
        self.widget.set_from_file(_icon)

    def _set_icon(self, path):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, 
                settings.DEFAULT_ICON_SIZE,
                settings.DEFAULT_ICON_SIZE)
        except Exception, e:
            print e
            return str(e)
            
        if pixbuf is not None:
            self.widget.set_from_pixbuf(pixbuf)
            

    def set_data(self, value):
        self._real_value = value
        if '/' in value:
            path = value
            self.widget.set_from_file(value)
        else:
            path = self._search_icon(value)
        return self._set_icon(path)

    def get_data(self):
        if hasattr(self, '_real_value'):
            return self._real_value
        else:
            prop = self.widget.get_property('file')
            if prop is not None:
                return prop
            return self.widget.get_property('icon-name')    
                
class WidgetFactory(object):

    def __init__(self, builder):
        self.builder = builder
        self._cache = {}
        
    def get(self, name, klass=None, defaulter=None, *args, **kwargs):

        if name not in self._cache:
            widget = self.builder.get_object(name)
            if klass is RAW:
                return widget
            if klass is None:
                try:
                    klass = _WIDGET_REGISTRY[type(widget)]
                except KeyError:
                    raise KeyError("'%s': Class %s not registered."%(name, type(widget)))
            if defaulter is None:
                defaulter_class = _DEFAULTER_REGISTRY.get(type(widget), None)
                if defaulter_class is not None:
                    defaulter = defaulter_class()
            
            self._cache[name]=klass(widget, defaulter, *args, **kwargs)
        return  self._cache[name]
        
    def __getitem__(self, index):
        return self.get(index)

