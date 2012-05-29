#-*- coding: utf-8-*-
from gi.repository import Gtk, GdkPixbuf, GLib

statusbar = None

class Status(object):

    def __init__(self, msg, end_msg=None, delay=3000):
        self.msg = msg
        self.end_msg = end_msg
        self.delay = delay
        self.context = statusbar.get_context_id('')


    def set_end_msg(self, msg):
        self.end_msg = msg
        
    def __enter__(self):
        statusbar.push(self.context, self.msg)
        return self

    def __exit__(self, *args):
        if self.end_msg is not None:
            statusbar.pop(self.context)
            statusbar.push(self.context, self.end_msg)
        GLib.timeout_add(self.delay, 
                         lambda *args: statusbar.pop(self.context))

            


def init(widget):
    global statusbar    
    statusbar = widget


    

    
    

