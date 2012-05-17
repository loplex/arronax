#-*- coding: utf-8-*-

import widgets, settings, desktopfile
from converter import Converter as DefaultConverter

class Connection(object):
    def __init__(self, data_store, data_key, widget, 
                 converter=None, validator=None):
        self.data_store = data_store
        self.data_key = data_key
        self.widget = widget
        if converter is None:
            self.converter = DefaultConverter()
        else:
            self.converter = converter
        self.validator = validator
        

    def get_widget(self):
        return self.widget

    def _get_raw_value(self):
        try:
            value = self.data_store[self.data_key]
        except Exception, e:
            print 'get_value: %s (%s)'%(e, self.data_key)
        return value
 
    def get_value(self):
        value = self._get_raw_value()
        return self.converter.rev_convert(value)

    def get_widget_value(self):
        try:
            return self.converter.convert(self.get_widget().get_data())
        except Exception, e:
            print 'get_widget_value: %s (%s)'%(e, self.data_key)

    
    def set_widget_value(self, value):
        value = self.converter.rev_convert(value)
        try:
            self.get_widget().set_data(value)
        except Exception, e:
            print 'set_widget_value: %s (%s)'%(e, value)

    def set_value(self, value):
        try:
            value = self.converter.convert(value)
            self.data_store[self.data_key] = value
        except Exception, e:
            print 'set_value: %s (%s)'%(e, value)

    def is_dirty(self):        
        try:
            return self._get_raw_value() != self.get_widget_value()
        except Exception, e:
            print 'is dirty: %s (%s=%s [%s])'%(e, self.data_key, self.get_widget_value(), bool(self.get_widget_value()))
            return None

    def has_key(self, key):
        return self.data_key == key

    def view(self):
        value = self.get_value()
        try:
            self.get_widget().set_data(value)
        except Exception, e:
            print 'view %s: %s (%s)'%(self.data_key, e, value)


    def store(self):      
        self.set_value(self.get_widget().get_data())

    def clear(self, store=False):
        self.get_widget().clear()
        if store:
            self.store()

    def __repr__(self):
        return '<Connection key=%s>'% self.data_key
                    


class ConnectionGroup(object):
    def __init__(self, data_store):
        self.data_store = data_store
        self.connections = []
                    
    def add(self, data_key, widget, converter=None, validator=None, 
            type=str):
        self.data_store.set_type_for_key(data_key, type)
        conn = Connection(self.data_store, data_key, widget,
                          converter=converter, 
                          validator=validator)
        self.connections.append(conn)


    def is_dirty(self):
        for conn in self.connections:
            if conn.is_dirty():
                return True
        return False

    def view(self):
        for conn in self.connections:
            conn.view()

    def store(self):
        for conn in self.connections:
            conn.store() 


    def clear(self, store=False):
        for conn in self.connections:
            conn.clear(store) 


