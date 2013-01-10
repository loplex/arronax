#-*- coding: utf-8-*-

import widgets, settings, desktopfile
from converter import Converter as DefaultConverter


class Connection(object):
    def __init__(self, data_store, data_key, widget, 
                 converter=None, validator=None, tags=None, active=True):
        self.data_store = data_store
        self.data_key = data_key
        self.widget = widget
        if converter is None:
            self.converter = DefaultConverter()
        else:
            self.converter = converter
        self.validator = validator
        if tags is None:
            self.tags = set()
        else:
            self.tags = set(tags)
        self.active = active

        

    def get_widget(self):
        return self.widget

    def _get_raw_value(self):
        try:
            value = self.data_store[self.data_key]
        except Exception, e:
            print 'get_value: %s (%s)'%(e, self.data_key)
        return value
 
    def _tags_match(self, tags):
        return len(self.tags.intersection(tags)) > 0
        
    def has_tag(self, tag):
        return tag in self.tags

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
            if self.active:
                value = self.converter.convert(value)
            else:
                value = desktopfile.FIELD_NOT_USED
            self.data_store[self.data_key] = value
        except Exception, e:
            print 'set_value: %s (%s)'%(e, value)

    def is_dirty(self):
        try:
            old_value = self.converter.convert(self.get_value())
            cur_value =  self.get_widget_value()
            return not self.converter.is_equal(old_value, cur_value)
        except Exception, e:
            print 'is dirty: %s (%s=%s [%s])'%(e, self.data_key)
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

    def show(self):
        self.get_widget().show()

    def hide(self):
        self.get_widget().hide()
  
    def switch(self, value):
        self.active = bool(value)
        self.get_widget().activate(self.active)


    def __repr__(self):
        return '<%s key=%s>'% (self.__class__.__name__, self.data_key)
                    

class NoDataConnection(Connection):
     def __init__(self, widget, tags=None):
         Connection.__init__(self, data_store=None, data_key=None, 
                             widget=widget, tags=tags)
         
     def _get_raw_value(self):   
         pass

     def get_value(self):
         pass

     def get_widget_value(self):
         pass

     def set_widget_value(self, value):
         pass

     def set_value(self, value):
         pass

     def is_dirty(self):
         return False
     
     def view(self):
         pass

     def store(self):
         pass

     def clear(self, store=False):   
         pass


class ConnectionGroup(object):
    def __init__(self, data_store):
        self.data_store = data_store
        self.connections = []
                 
    
    def add(self, data_key, widget, 
             converter=None, validator=None, 
             type=str, tags=None, related=None):
        self.data_store.set_type_for_key(data_key, type)
        conn = Connection(self.data_store, data_key, widget,
                          converter=converter, 
                          validator=validator,
                          tags=tags)
        self.connections.append(conn)
        if related is not None:
            if isinstance(related, widgets.WidgetBase):
                related = [related]
            for r in related:
                self.add_no_data(r, tags)


    def add_no_data(self, widget, tags=None):
        conn = NoDataConnection(widget, tags=tags)
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


    def switch(self, tags, value):
        for tag, func in tags.iteritems():
            val = func(value)
            for conn in self.connections:
                if conn.has_tag(tag):
                    conn.switch(val)


