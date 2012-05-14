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

from gi.repository import Gtk, Gdk, GdkPixbuf

_REGISTRY = {}

RAW = object()


class WidgetMeta(type):
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        wraps = getattr(cls, '__wraps__', ())
        for w in wraps:
            _REGISTRY[w] = cls


class WidgetBase(object):
    __metaclass__ = WidgetMeta
    __wraps__ = (Gtk.Grid,)

    def __init__(self, widget):
        self.widget = widget

    def get_data(self, value):
        pass
    
    def set_data(elf, data):
        pass

    def hide(self):
        self.widget.hide()

    def show(self):
        self.widget.show_all()

      

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

    def set_data(self, value):
        self.widget.set_property('file', value)

    def get_data(self):
        print 'PROP:',  self.widget.get_property('file'), self.widget.get_property('icon-name')
        prop = self.widget.get_property('file')
        if prop is not None:
            return prop
        return self.widget.get_property('icon-name')

    
                
class WidgetFactory(object):

    def __init__(self, builder, help_func=None):
        self.builder = builder
        self.help_func = help_func
        self._cache = {}
        
    def get(self, name, help=None, klass=None):

        if name not in self._cache:
            widget = self.builder.get_object(name)
            if klass is RAW:
                return widget
            if klass is None:
                try:
                    klass = _REGISTRY[type(widget)]
                except KeyError:
                    raise KeyError("'%s': Class %s not registered."%(name, type(widget)))
            if help:
                widget.set_property("has-tooltip", True)
                def func(w, e, *args):
                    self.help_func(help)
                    return False
                widget.connect('query-tooltip', func)
            self._cache[name]=klass(widget)
        return  self._cache[name]
        
    def __getitem__(self, index):
        return self.get(index)

